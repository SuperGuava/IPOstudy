# Session Handoff

Updated: 2026-02-18 09:45 (+09:00)

## Goal

Allow any new session to resume development without prior chat context.

## Verification Lock

- Primary checkpoint: `docs/operations/verification-lock.md`
- If lock conditions are unchanged, do not re-run probe/refresh loops.
- Re-run only when lock says rerun is required.

## Environment Bootstrap

1. `docker compose -f infra/docker-compose.yml up -d`
2. `cd backend && python -m alembic upgrade head`
3. `cd backend && python -m pytest -q`
4. `cd web && npm install`
5. `cd web && npm run build:stable`

## Deploy Bootstrap (Production Compose)

1. `cd D:\260214`
2. `docker compose -f infra/docker-compose.prod.yml up -d --build`
3. `docker compose -f infra/docker-compose.prod.yml ps`
4. `docker compose -f infra/docker-compose.prod.yml logs -f backend`

## Runtime Launch

1. Backend:
   - `cd backend`
   - `python -m uvicorn app.main:app --host 0.0.0.0 --port 8000`
2. Web:
   - `cd web`
   - `npm run dev -- -p 3000`

## Smoke Checklist

1. `GET /api/v1/health` -> `{"status":"ok"}`
2. `GET /api/v1/ipo/pipeline`
3. `GET /api/v1/ipo/pipeline?refresh=true&corp_code=00126380&bas_dd=20250131`
4. `GET /api/v1/insights/companies?limit=20`
5. `GET /api/v1/insights/templates`
6. `GET /api/v1/insights/overview`
7. `GET /api/v1/insights/compare?company_key=name:3R&company_key=name:3S`
8. `GET /api/v1/insights/report?company_key=name:3R&template_id=foundation-check`
9. `GET /api/v1/quality/issues`
10. `GET /api/v1/quality/summary`
11. `GET /api/v1/quality/overview`
12. `GET /api/v1/quality/rules`
13. `cd backend && python scripts/krx_openapi_probe.py`

## KRX Current Status

- Multi-path config is enabled for all categories.
- Expected probe baseline:
  - `index/stock/securities/bond/derivative/general`: mostly `OK`
  - `esg`: `partial`
- ESG pending approvals:
  - `esg/esg_index_info`
  - `esg/esg_etp_info`
- `esg/sri_bond_info` is active.
- `refresh=true` response includes `source_status_detail` for category/path-level diagnostics.

## Stability Notes

- Web build:
  - use `cd web && npm run build:stable`
  - do not run build and Playwright in parallel during triage.
  - if build shows `spawn EPERM` in restricted shells, rerun in a full-permission terminal.
- KRX:
  - intermittent `403 Access Denied` can occur.
  - backend refresh path retries transient `Access Denied` responses.
- KIND:
  - real rows are loaded via `searchPubofrProgComSub` and parser supports that path.
- Snapshot publish:
  - publish path replaces previous `ipo_pipeline_item` snapshot rows to prevent stale demo leftovers.
- Local API check:
  - if `refresh.source_status` shows `missing_key` for all sources, verify you are not hitting a stale/orphan backend container on `:8000`.
  - run local backend with `.env` loaded when validating refresh behavior.

## Current Reference Numbers (2026-02-17)

1. `cd backend && python -m pytest -q` -> `80 passed`
2. `cd backend && python scripts/krx_openapi_probe.py --repeat 5 --bas-dd 20250131 --strict-categories stock,esg` ->
   - `stock`: `OK` (all 5/5)
   - `esg`: `partial` (`esg/sri_bond_info=OK`, `esg/esg_index_info=AUTH ERROR`, `esg/esg_etp_info=AUTH ERROR`)
3. `GET /api/v1/ipo/pipeline?refresh=true&corp_code=00126380&bas_dd=20250131` repeated 5 times
   (local backend with `.env` loaded, `127.0.0.1:8010`) ->
   - all runs `published=True`
   - all runs `kind_rows=2301`, `dart_rows=100`, `krx_rows=12`
   - all runs `source_status.esg=partial:ok=2262,auth=2,denied=0,schema=0,error=0`
4. `GET /api/v1/ipo/pipeline` -> `total=2301` (no `alpha-tech`)

## Where To Read First

1. `guava_guide.md`
2. `docs/operations/deployment.md`
3. `docs/operations/vercel-render-deploy.md`
4. `docs/operations/runbook.md`
5. `docs/operations/history.md`
6. `docs/operations/verification-lock.md`

## Recommended Next Task

1. Confirm/complete ESG approval for `esg/esg_index_info` and `esg/esg_etp_info` in KRX portal.
2. After approval, re-run strict probe and refresh loop (`x5`) to verify `esg` becomes full `OK`.
3. If ESG becomes all-OK, update:
   - `docs/operations/runbook.md`
   - `docs/operations/history.md`
   - `guava_guide.md`
