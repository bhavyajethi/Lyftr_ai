# Containerized Webhook API

- Docker Desktop (recommended for evaluation / production-style run)
- Python (for local runs and signature helper snippets)

## Configuration (12-factor)

The service is configured only via environment variables:

- `WEBHOOK_SECRET` (required for readiness)
- `DATABASE_URL` (required)
- `LOG_LEVEL` (optional, default `INFO`)

Recommended `.env` for Docker:

```env
WEBHOOK_SECRET=mysecretkey
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

- Swagger UI: `http://localhost:8000/docs`

To run the unit tests against the container:
- Run unittest: `python -m unittest discover tests`

## Environment variables

- DATABASE_URL
- WEBHOOK_SECRET
- LOG_LEVEL

Example:

- DATABASE_URL=sqlite:////data/app.db
- WEBHOOK_SECRET=testsecret
- LOG_LEVEL=INFO
