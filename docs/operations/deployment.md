# Deployment Guide (Docker Compose)

Updated: 2026-02-17

## 1) Preconditions

1. Docker Desktop is running.
2. Repository root:
   - `cd D:\260214`
3. `.env` contains:
   - `DART_API_KEY`
   - `KRX_API_KEY`

## 2) Start Production Stack

1. Build and start:
   - `docker compose -f infra/docker-compose.prod.yml up -d --build`
2. Check status:
   - `docker compose -f infra/docker-compose.prod.yml ps`
3. Check logs:
   - `docker compose -f infra/docker-compose.prod.yml logs -f backend`
   - `docker compose -f infra/docker-compose.prod.yml logs -f web`

## 3) Verify

1. API health:
   - `http://127.0.0.1:8000/api/v1/health`
2. Web:
   - `http://127.0.0.1:3000`
3. Smoke APIs:
   - `GET /api/v1/insights/overview`
   - `GET /api/v1/ipo/pipeline`
   - `GET /api/v1/quality/overview`

## 4) Stop / Restart

1. Stop:
   - `docker compose -f infra/docker-compose.prod.yml down`
2. Restart:
   - `docker compose -f infra/docker-compose.prod.yml up -d`

## 5) Notes

1. Backend container runs Alembic migration at startup.
2. Web container uses `API_BASE_URL=http://backend:8000/api/v1` internally.
3. Browser-side fallback is `NEXT_PUBLIC_API_BASE_URL` (default `http://localhost:8000/api/v1`).

