# Anti-Gravity IPO Fast Fetch

Modular monolith for Korean IPO and company snapshot data using DART, KIND, and KRX sources.

## Repository Layout

- `backend/`: FastAPI service, connectors, ETL, jobs, and tests
- `web/`: Next.js dashboard and E2E tests
- `infra/`: local infrastructure compose file
- `docs/`: plans, API spec, and operational runbook

## Local Setup

0. Move to repository root first:
   - `cd D:\260214`
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

## Deploy (Docker)

1. Move to repository root:
   - `cd D:\260214`
2. Ensure `.env` has production keys (`DART_API_KEY`, `KRX_API_KEY`) and optional port overrides:
   - `BACKEND_PORT`, `WEB_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
3. Build and start production stack:
   - `docker compose -f infra/docker-compose.prod.yml up -d --build`
4. Check status:
   - `docker compose -f infra/docker-compose.prod.yml ps`
5. Check logs:
   - `docker compose -f infra/docker-compose.prod.yml logs -f backend`
   - `docker compose -f infra/docker-compose.prod.yml logs -f web`
6. Open:
   - Web: `http://127.0.0.1:3000`
   - API health: `http://127.0.0.1:8000/api/v1/health`

## Operations Docs

- Runbook: `docs/operations/runbook.md`
- Deployment guide: `docs/operations/deployment.md`
- Public deploy (Vercel + Render): `docs/operations/vercel-render-deploy.md`
- Verification lock: `docs/operations/verification-lock.md`
- Execution history: `docs/operations/history.md`
- Session handoff: `docs/operations/session-handoff.md`
- Owner summary: `guava_guide.md`

## Core Endpoints

- `GET /api/v1/company/snapshot?corp_code=<corp_code>`
- `GET /api/v1/company/{corp_code}/financials`
- `GET /api/v1/ipo/pipeline`
- `GET /api/v1/ipo/pipeline?refresh=true&corp_code=00126380&bas_dd=20260215`
- `GET /api/v1/ipo/{pipeline_id}`
- `GET /api/v1/insights/companies?query=<name_or_code>&limit=30`
- `GET /api/v1/insights/company?company_key=<company_key>`
- `GET /api/v1/insights/templates`
- `GET /api/v1/insights/overview`
- `GET /api/v1/insights/compare?company_key=<k1>&company_key=<k2>`
- `GET /api/v1/insights/report?company_key=<k1>&template_id=foundation-check`
- `GET /api/v1/export/ipo.xlsx`
- `GET /api/v1/export/company/{corp_code}.xlsx`
- `GET /api/v1/quality/issues`
- `GET /api/v1/quality/summary`
- `GET /api/v1/quality/overview`
- `GET /api/v1/quality/rules`
- `GET /api/v1/quality/entity/{entity_key}`

## Product UI Scope

- `Dashboard` page is API-backed (`/ipo/pipeline`, `/quality/issues`, `/quality/summary`).
- `Company Explorer` page is API-backed (`/insights/companies`, `/insights/company`, `/insights/templates`).
- `Company Explorer` supports stage/risk filters, multi-company compare, and template-based beginner reports.
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
