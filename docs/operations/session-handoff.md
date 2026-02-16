# Session Handoff

Updated: 2026-02-16

## Goal

다른 세션/다른 작업자도 즉시 같은 상태에서 개발을 이어갈 수 있도록 실행 순서, 검증 기준, 현재 리스크를 고정한다.

## Environment Bootstrap

1. `docker compose -f infra/docker-compose.yml up -d`
2. `cd backend && python -m alembic upgrade head`
3. `cd backend && python -m pytest -q`
4. `cd web && npm install`
5. `cd web && npm run build:stable`

## Runtime Launch

1. Backend:
   - `cd backend`
   - `uvicorn app.main:app --host 0.0.0.0 --port 8000`
2. Web:
   - `cd web`
   - `npm run dev -- --port 3000`

## Smoke Checklist

1. `GET /api/v1/health` -> `{"status":"ok"}`
2. `GET /api/v1/ipo/pipeline`
3. `GET /api/v1/ipo/pipeline?refresh=true&corp_code=00126380&bas_dd=20250131`
4. `GET /api/v1/quality/issues`
5. `GET /api/v1/quality/summary`
6. `cd backend && python scripts/krx_openapi_probe.py`

## KRX Current Status

- Multi-path config is enabled for all categories.
- Expected probe baseline:
  - `index/stock/securities/bond/derivative/general`: mostly `OK`
  - `esg`: `partial`
- ESG pending approvals:
  - `esg/esg_index_info`
  - `esg/esg_etp_info`
- `esg/sri_bond_info` is active.

## Stability Notes

- Web build:
  - use `cd web && npm run build:stable`
  - do not run build and Playwright in parallel during triage.
- KRX:
  - intermittent `403 Access Denied` can occur.
  - backend refresh path includes retry for transient `Access Denied`.

## Where To Read First

1. `guava_guide.md`
2. `docs/operations/runbook.md`
3. `docs/operations/history.md`
4. `docs/plans/2026-02-15-antigravity-productization-design.md`
5. `docs/plans/2026-02-15-antigravity-productization.md`

## Recommended Next Task

1. ESG portal approval completion check
2. `krx_openapi_probe.py` + refresh API re-verify
3. If ESG becomes all-OK, update:
   - `docs/operations/runbook.md`
   - `docs/operations/history.md`
   - `guava_guide.md`
