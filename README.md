# Containerized Webhook API
![alt text]({4C7CEE95-2A34-4C96-9B72-162FAA033630}.png)
## Setup Used

VSCode + Cursor + Windsurf 

## Project structure

```
/app
  main.py          # FastAPI app, middleware, routes
  models.py        # Pydantic models + validation
  storage.py       # SQLite schema + DB operations
  logging_utils.py # JSON logging helpers
  metrics.py       # Minimal Prometheus-style metrics
  config.py        # Environment config loading
/tests
  test_webhook.py
  test_messages.py
  test_stats.py
app.db
Dockerfile
docker-compose.yml
Makefile
requirements.txt
README.md
.env
```

## Requirements

- Docker Desktop (recommended for evaluation / production-style run)
- Python (for local runs and signature helper snippets)

## Configuration (12-factor)

The service is configured only via environment variables:

- `WEBHOOK_SECRET` (required for readiness)
- `DATABASE_URL` (required)
- `LOG_LEVEL` (optional, default `INFO`)

Recommended `.env` for Docker:

```env
WEBHOOK_SECRET=testsecret
DATABASE_URL=sqlite:////app/app.db
LOG_LEVEL=INFO
```

Notes:

- `DATABASE_URL=sqlite:////app/app.db` is a Docker path (volume-mounted).

## How to run (Docker Compose)

- Start: `docker compose up --build`
- Check Health: `http://localhost:8000/health/ready`
- Stop the Service: `Ctrl+c`

Service base URL:

- `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`

## Environment variables

- DATABASE_URL
- WEBHOOK_SECRET
- LOG_LEVEL

Example:

DATABASE_URL=sqlite:////data/app.db
WEBHOOK_SECRET=testsecret
LOG_LEVEL=INFO

## Endpoints

- POST /webhook
- GET /messages
- GET /stats
- GET /metrics
- GET /health/live
- GET /health/ready

## API Endpoints (PowerShell examples)

### 1) POST /webhook

Request body example: JSON (message_id, from, to, ts, text)
Behavior: Idempotent (ignores duplicates without error).

### 2) GET /messages

Query params:

- `limit` (default 50, min 1, max 100)
- `offset` (default 0, min 0)
- `from` 
- `since` 
- `q` ('search text`)

Retrieve stored messages with filtering.
- Params: limit, offset, from, since, q (search text).

### 3) GET /stats


Returns:

- `total_messages`
- `unique_senders`
- `top 10 senders`
- `timestamp_range`

### 4) GET /metrics

```powershell
curl.exe -s "http://localhost:8000/metrics"
```
Return:
- `Prometheus format metrics`

## How to run locally (no Docker)

This is useful if you want to test visually in the browser.

1) Create `.env`:

```env
WEBHOOK_SECRET=mysecretkey
DATABASE_URL=sqlite:///./local.db
LOG_LEVEL=INFO
```

2) Install deps:

```sh
pip install -r requirements.txt
```

3) Run:

```sh
uvicorn app.main:app --reload --env-file .env
```

Open:

- `Access: http://127.0.0.1:8000`

Notes:

- If Docker is running on port 8000, use a different port for local runs (like 8001), or stop Docker first.

## Logging

Logs are one JSON object per line (good for `jq`), including:

- `ts` 
- `level`
- `info`
- `request_id` 
- `method`, `path`, `status`, `latency_ms`

## Design decisions

### HMAC verification

- Computes `HMAC_SHA256(WEBHOOK_SECRET, raw_request_body_bytes)`.

### Exactly-once ingest / idempotency

- SQLite enforces uniqueness with `PRIMARY KEY (message_id)`.
- Duplicate inserts are handled gracefully (no stack traces) and still return `200 {"status":"ok"}`.

### Metrics

Exposes a minimal Prometheus-style text endpoint at `/metrics`.
