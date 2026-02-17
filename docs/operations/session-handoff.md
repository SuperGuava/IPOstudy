# Session Handoff

Updated: 2026-02-17

## Goal

Allow any new session to resume development without prior chat context.

## Environment Bootstrap

1. `docker compose -f infra/docker-compose.yml up -d`
2. `cd backend && python -m alembic upgrade head`
3. `cd backend && python -m pytest -q`
4. `cd web && npm install`
5. `cd web && npm run build:stable`

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
- KRX:
  - intermittent `403 Access Denied` can occur.
  - backend refresh path retries transient `Access Denied` responses.
- KIND:
  - real rows are loaded via `searchPubofrProgComSub` and parser supports that path.
- Snapshot publish:
  - publish path replaces previous `ipo_pipeline_item` snapshot rows to prevent stale demo leftovers.

## Current Reference Numbers (2026-02-17)

1. `cd backend && python -m pytest -q` -> `67 passed`
2. `GET /api/v1/ipo/pipeline?refresh=true&corp_code=00126380&bas_dd=20250131` ->
   - `status=200`
   - `refresh.published=true`
   - `refresh.kind_rows=2301`
3. `GET /api/v1/ipo/pipeline` -> `total=2301` (no `alpha-tech`)

## Where To Read First

1. `guava_guide.md`
2. `docs/operations/runbook.md`
3. `docs/operations/history.md`
4. `docs/plans/2026-02-15-antigravity-productization-design.md`
5. `docs/plans/2026-02-15-antigravity-productization.md`

## Recommended Next Task

1. Confirm ESG approval for `esg/esg_index_info` and `esg/esg_etp_info`.
2. Re-run `krx_openapi_probe.py` and refresh API 5 times.
3. If ESG becomes all-OK, update:
   - `docs/operations/runbook.md`
   - `docs/operations/history.md`
   - `guava_guide.md`
