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
   - `python -m uvicorn app.main:app --reload --port 8000`
3. Web:
   - `cd web`
   - `npm install`
   - (optional) set `NEXT_PUBLIC_API_BASE_URL` in root `.env`
   - `npm run dev -- -p 3000`

## Operations Docs

- Runbook: `docs/operations/runbook.md`
- Execution history: `docs/operations/history.md`
- Session handoff: `docs/operations/session-handoff.md`
- Owner summary: `guava_guide.md`

## Core Endpoints

- `GET /api/v1/company/snapshot?corp_code=<corp_code>`
- `GET /api/v1/company/{corp_code}/financials`
- `GET /api/v1/ipo/pipeline`
- `GET /api/v1/ipo/pipeline?refresh=true&corp_code=00126380&bas_dd=20260215`
- `GET /api/v1/ipo/{pipeline_id}`
- `GET /api/v1/export/ipo.xlsx`
- `GET /api/v1/export/company/{corp_code}.xlsx`
- `GET /api/v1/quality/issues`
- `GET /api/v1/quality/summary`
- `GET /api/v1/quality/overview`
- `GET /api/v1/quality/rules`
- `GET /api/v1/quality/entity/{entity_key}`

## Product UI Scope

- `Dashboard` page is API-backed (`/ipo/pipeline`, `/quality/issues`, `/quality/summary`).
- `Dashboard` includes stage mix and fail-rate trend bars.
- `Quality` page is API-backed (`/quality/issues`, `/quality/summary`).
- `Quality` supports query filters (`source`, `severity`, `from`, `to`).
- `IPO Pipeline` page supports live refresh query flow.

## Data Quality Gate

- Source rule packs: DART / KIND / KRX / Cross-source.
- Rule dictionary endpoint: `/api/v1/quality/rules` (human-readable meaning + operator action)
- Gate behavior:
  - `PASS`: publish snapshot
  - `WARN`: publish + record issue
  - `FAIL`: block publish and keep previous snapshot

## Verification

- Backend: `cd backend && python -m pytest -q`
- Web unit placeholder: `cd web && npm test`
- Web e2e: `cd web && npx playwright test`
- Web build (stable): `cd web && npm run build:stable`
- One-shot ETL: `cd backend && python scripts/run_pipeline_once.py --corp-code 00126380`
- IPO refresh smoke:
  - `GET /api/v1/ipo/pipeline?refresh=true&corp_code=00126380&bas_dd=20250131`
  - then `GET /api/v1/ipo/pipeline` should return multi-row snapshot (not single demo row).

## KRX Open API Check

- `cd backend && python scripts/krx_openapi_probe.py`
- Repeat strict check example:
  - `cd backend && python scripts/krx_openapi_probe.py --repeat 5 --bas-dd 20250131 --strict-categories stock,esg`
- If output is `AUTH ERROR`, complete API key issuance and API usage approval on KRX Open API portal.

## KRX Category Expansion

- Configure additional KRX Open API paths in `.env`:
  - `KRX_API_INDEX_PATH`
  - `KRX_API_STOCK_PATH`
  - `KRX_API_SECURITIES_PATH`
  - `KRX_API_BOND_PATH`
  - `KRX_API_DERIVATIVE_PATH`
  - `KRX_API_GENERAL_PATH`
  - `KRX_API_ESG_PATH`
- Each `KRX_API_*_PATH` supports comma-separated multiple paths.
