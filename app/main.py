import hmac
import hashlib
import time
import uuid
import re
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException, Depends, Query, Response
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc, text
from sqlalchemy.exc import IntegrityError

from app.config import get_settings
from app.storage import get_db, init_db
from app.models import Message
from app.logging_utils import logger
from app.metrics import inc_counter, generate_latest

app = FastAPI()
settings = get_settings()

# --- PYDANTIC MODEL (Moved from schemas.py) ---
class WebhookPayload(BaseModel):
    message_id: str = Field(..., min_length=1)
    from_: str = Field(..., alias="from")
    to: str
    ts: str
    text: str | None = Field(default=None, max_length=4096)

    @validator('from_', 'to')
    def validate_msisdn(cls, v):
        if not re.match(r'^\+\d+$', v):
            raise ValueError('Must be E.164 format')
        return v

    class Config:
        populate_by_name = True

@app.on_event("startup")
def on_startup():
    init_db()

# --- MIDDLEWARE ---
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    response = await call_next(request)
    
    process_time = (time.time() - start_time) * 1000
    
    inc_counter("http_requests_total", {
        "path": request.url.path,
        "method": request.method,
        "status": str(response.status_code)
    })
    
    if request.url.path != "/metrics":
        logger.info("Request processed", extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "latency_ms": round(process_time, 2)
        })
        
    return response

# --- HELPER: Signature ---
async def verify_signature(request: Request):
    signature = request.headers.get("X-Signature")
    if not signature:
        inc_counter("webhook_requests_total", {"result": "invalid_signature"})
        logger.error("Missing signature", extra={"result": "invalid_signature"})
        raise HTTPException(status_code=401, detail="invalid signature")

    body = await request.body()
    expected_sig = hmac.new(
        settings.WEBHOOK_SECRET.encode(), body, hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(signature, expected_sig):
        inc_counter("webhook_requests_total", {"result": "invalid_signature"})
        logger.error("Invalid signature", extra={"result": "invalid_signature"})
        raise HTTPException(status_code=401, detail="invalid signature")

# --- ROUTES ---

@app.post("/webhook")
async def receive_webhook(
    payload: WebhookPayload, 
    request: Request,
    db: Session = Depends(get_db),
    _ = Depends(verify_signature)
):
    try:
        new_msg = Message(
            message_id=payload.message_id,
            from_msisdn=payload.from_,
            to_msisdn=payload.to,
            ts=payload.ts,
            text=payload.text,
            created_at=datetime.utcnow().isoformat() + "Z"
        )
        db.add(new_msg)
        db.commit()
        
        inc_counter("webhook_requests_total", {"result": "created"})
        logger.info("Webhook accepted", extra={
            "request_id": request.state.request_id,
            "message_id": payload.message_id,
            "dup": False,
            "result": "created"
        })
        return {"status": "ok"}

    except IntegrityError:
        db.rollback()
        inc_counter("webhook_requests_total", {"result": "duplicate"})
        logger.info("Duplicate webhook", extra={
            "request_id": request.state.request_id,
            "message_id": payload.message_id,
            "dup": True,
            "result": "duplicate"
        })
        return {"status": "ok"}

@app.get("/messages")
def list_messages(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    from_: str | None = Query(None, alias="from"),
    since: str | None = None,
    q: str | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(Message)
    if from_: query = query.filter(Message.from_msisdn == from_)
    if since: query = query.filter(Message.ts >= since)
    if q: query = query.filter(Message.text.ilike(f"%{q}%"))

    total = query.count()
    query = query.order_by(asc(Message.ts), asc(Message.message_id))
    messages = query.offset(offset).limit(limit).all()

    data = [{
        "message_id": m.message_id,
        "from": m.from_msisdn,
        "to": m.to_msisdn,
        "ts": m.ts,
        "text": m.text
    } for m in messages]

    return {"data": data, "total": total, "limit": limit, "offset": offset}

@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    total_messages = db.query(func.count(Message.message_id)).scalar()
    if total_messages == 0:
        return {
            "total_messages": 0, "senders_count": 0, 
            "messages_per_sender": [], "first_message_ts": None, "last_message_ts": None
        }

    senders_count = db.query(func.count(func.distinct(Message.from_msisdn))).scalar()
    
    top_senders = (
        db.query(Message.from_msisdn, func.count(Message.message_id).label("count"))
        .group_by(Message.from_msisdn)
        .order_by(desc("count"))
        .limit(10)
        .all()
    )
    messages_per_sender = [{"from": row.from_msisdn, "count": row.count} for row in top_senders]

    min_ts = db.query(func.min(Message.ts)).scalar()
    max_ts = db.query(func.max(Message.ts)).scalar()

    return {
        "total_messages": total_messages,
        "senders_count": senders_count,
        "messages_per_sender": messages_per_sender,
        "first_message_ts": min_ts,
        "last_message_ts": max_ts
    }

@app.get("/health/live")
def live():
    return {"status": "ok"}

@app.get("/health/ready")
def ready(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        raise HTTPException(status_code=503, detail="Database not ready")
    if not settings.WEBHOOK_SECRET:
        raise HTTPException(status_code=503, detail="Secret not set")
    return {"status": "ready"}

@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type="text/plain")