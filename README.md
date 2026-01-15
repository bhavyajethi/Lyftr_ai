# 📦 Containerized Webhook API

A production-style, Dockerized **FastAPI** service that securely ingests webhooks, stores them exactly once in **SQLite**, and exposes analytics, metrics, and health probes.  
Designed to meet real-world backend evaluation standards with idempotency, HMAC verification, structured logs, and Prometheus-style metrics.

---

## 🧱 Features

- 🔐 **HMAC-SHA256 Signature Verification** for all incoming webhooks  
- 🧮 **Exactly-once ingestion (Idempotency)** via unique `message_id`  
- 📊 **Analytics Endpoint** (`/stats`)  
- 📄 **Paginated & Filterable Listing** (`/messages`)  
- 📈 **Prometheus Metrics** (`/metrics`)  
- 🩺 **Health Checks** (`/health/live`, `/health/ready`)  
- 🧾 **Structured JSON Logging**  
- 🐳 **Fully Containerized with Docker Compose**

---

## 📂 Project Structure

```text
/
├── app/
│   ├── main.py          # FastAPI app, middleware, routes, & Pydantic models
│   ├── storage.py       # SQLite connection & initialization
│   ├── logging_utils.py # JSON logging helpers
│   ├── metrics.py       # Minimal Prometheus-style metrics
│   └── config.py        # Environment config loading
├── tests/
│   ├── test_webhook.py
│   ├── test_messages.py
│   └── test_stats.py
├── app.db              
├── Dockerfile          
├── docker-compose.yml   
├── Makefile            
├── requirements.txt     
└── .env

⚙️ Environment Configuration (MANDATORY)

Create a .env file in the project root with the following:

WEBHOOK_SECRET=mysecretkey
DATABASE_URL=sqlite:////app/app.db
LOG_LEVEL=INFO


⚠️ Important

WEBHOOK_SECRET must be set. If missing, /health/ready will fail.

DATABASE_URL points to the SQLite file inside the container.

🚀 Quick Start (Docker)
1️⃣ Build & Run
docker compose up --build

2️⃣ Access

API Base: http://localhost:8000

Swagger UI: http://localhost:8000/docs

3️⃣ Stop
Ctrl + C

🧪 Testing
▶ Automated Unit Tests
python -m unittest discover tests

🔗 API Usage
🔐 1. Ingest Webhook

POST /webhook

Requires HMAC-SHA256 signature of the raw JSON body in X-Signature.

➕ Generate Signature (Python One-liner)
python -c "import hmac, hashlib; print(hmac.new(b'mysecretkey', b'{\"message_id\":\"m1\",\"from\":\"+123\",\"to\":\"+456\",\"ts\":\"2025-01-01T10:00:00Z\",\"text\":\"Hello\"}', hashlib.sha256).hexdigest())"

➕ Send Request
curl -X POST "http://localhost:8000/webhook" \
  -H "Content-Type: application/json" \
  -H "X-Signature: <PASTE_SIGNATURE_HERE>" \
  -d '{"message_id":"m1","from":"+123","to":"+456","ts":"2025-01-01T10:00:00Z","text":"Hello"}'

✅ Success
{"status":"ok"}

❌ Invalid Signature
{"detail":"invalid signature"}

📄 2. List Messages

GET /messages

Supports pagination and filters.

Query Params
Param	Description
limit	Default 50, Max 100
offset	Default 0
from	Filter by sender
since	ISO-8601 timestamp
q	Search in text
Example
curl "http://localhost:8000/messages?limit=10&from=+123"

📊 3. Statistics

GET /stats

Returns:

total_messages

senders_count

messages_per_sender

first_message_ts

last_message_ts

curl "http://localhost:8000/stats"

📈 4. Metrics (Prometheus)

GET /metrics

curl "http://localhost:8000/metrics"


Includes:

http_requests_total{path,status}

webhook_requests_total{result}

Latency buckets

🩺 5. Health Checks
curl http://localhost:8000/health/live
curl http://localhost:8000/health/ready

Endpoint	Behavior
/health/live	Always 200 if app is running
/health/ready	200 only if DB reachable & WEBHOOK_SECRET set
⚙️ Design & Architecture
🗄 Persistence

SQLite database.

File-based DB (app.db) mounted into the container.

Data persists across restarts.

🔁 Idempotency

message_id is PRIMARY KEY.

Duplicate webhooks:

Not inserted again.

Still return 200 OK.

🔐 Security

HMAC validation:

HMAC-SHA256(secret=WEBHOOK_SECRET, message=<raw request body bytes>)


Invalid/missing signature → 401 Unauthorized.

📜 Observability

Structured JSON logs:
ts, level, request_id, path, status, latency_ms
Prometheus metrics at /metrics.

🛠 Local Development (WITHOUT Docker)
1️⃣ Install Dependencies
pip install -r requirements.txt

2️⃣ Update .env for Local Path
DATABASE_URL=sqlite:///./app.db

3️⃣ Run Server
uvicorn app.main:app --reload
