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
