# Anti-Gravity IPO Fast Fetch

Modular monolith for Korean IPO and company snapshot data using DART, KIND, and KRX sources.

## Repository Layout

- `backend/`: FastAPI service, connectors, ETL, jobs, and tests
- `web/`: Next.js dashboard and E2E tests
- `infra/`: local infrastructure compose file
- `docs/`: plans, API spec, and operational runbook

## Local Setup

1. Start infra:
   - `docker compose -f infra/docker-compose.yml up -d`
2. Backend:
   - `cd backend`
   - `python -m alembic upgrade head`
   - `python -m pytest -q`
   - `uvicorn app.main:app --reload --port 8000`
3. Web:
   - `cd web`
   - `npm install`
   - `npm run dev -- --port 3000`

## Core Endpoints

- `GET /api/v1/company/snapshot?corp_code=<corp_code>`
- `GET /api/v1/company/{corp_code}/financials`
- `GET /api/v1/ipo/pipeline`
- `GET /api/v1/ipo/{pipeline_id}`
- `GET /api/v1/export/ipo.xlsx`
- `GET /api/v1/export/company/{corp_code}.xlsx`
- `GET /api/v1/quality/issues`
- `GET /api/v1/quality/summary`
- `GET /api/v1/quality/entity/{entity_key}`

## Data Quality Gate

- Source rule packs: DART / KIND / KRX / Cross-source.
- Gate behavior:
  - `PASS`: publish snapshot
  - `WARN`: publish + record issue
  - `FAIL`: block publish and keep previous snapshot

## Verification

- Backend: `cd backend && python -m pytest -q`
- Web unit placeholder: `cd web && npm test`
- Web e2e: `cd web && npx playwright test`
