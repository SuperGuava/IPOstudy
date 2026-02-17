# Operations Runbook

See also: `docs/operations/session-handoff.md`, `docs/operations/history.md`, `guava_guide.md`

## Environment Variables

- `DART_API_KEY`
- `KRX_API_KEY`
- `DATABASE_URL`
- `REDIS_URL`
- `NEXT_PUBLIC_API_BASE_URL` (for web server-side fetch target)
- Optional KRX Open API category paths:
  - `KRX_API_INDEX_PATH`
  - `KRX_API_STOCK_PATH`
  - `KRX_API_SECURITIES_PATH`
  - `KRX_API_BOND_PATH`
  - `KRX_API_DERIVATIVE_PATH`
  - `KRX_API_GENERAL_PATH`
  - `KRX_API_ESG_PATH`
  - each variable supports comma-separated multiple paths.

Recommended validated paths (verified on 2026-02-16):

- `KRX_API_INDEX_PATH=idx/krx_dd_trd,idx/kospi_dd_trd,idx/kosdaq_dd_trd`
- `KRX_API_STOCK_PATH=sto/stk_bydd_trd`
- `KRX_API_SECURITIES_PATH=sto/ksq_bydd_trd,sto/ksq_isu_base_info`
- `KRX_API_BOND_PATH=bon/bnd_bydd_trd`
- `KRX_API_DERIVATIVE_PATH=drv/fut_bydd_trd,drv/opt_bydd_trd`
- `KRX_API_GENERAL_PATH=sto/knx_bydd_trd,sto/knx_isu_base_info`
- `KRX_API_ESG_PATH=esg/sri_bond_info,esg/esg_index_info,esg/esg_etp_info`

## Start Services

1. `docker compose -f infra/docker-compose.yml up -d`
2. Backend API:
   - `cd backend`
   - `python -m alembic upgrade head`
   - `python -m uvicorn app.main:app --host 0.0.0.0 --port 8000`
   - If shell env is not exported, load `.env` before startup (PowerShell):
     - `Get-Content ..\\.env | %{ if($_ -match '^[A-Za-z_][A-Za-z0-9_]*='){ $k,$v=$_.Split('=',2); [System.Environment]::SetEnvironmentVariable($k,$v,'Process') } }`
3. Worker (future Celery integration):
   - `cd backend`
   - `python -m app.jobs.celery_app`

## Beginner Troubleshooting

1. `uvicorn` not recognized in PowerShell:
   - Use module form, not bare command:
   - `python -m uvicorn app.main:app --host 0.0.0.0 --port 8000`
2. `npm run dev -- --port 3000` fails with `next dev 3000`:
   - Use:
   - `npm run dev -- -p 3000`
3. IPO list shows only one company:
   - Run one refresh call first:
   - `GET /api/v1/ipo/pipeline?refresh=true&corp_code=00126380&bas_dd=20250131`
   - Then check:
   - `GET /api/v1/ipo/pipeline`
   - Expected: large dataset (current reference about 2,300 rows), demo row `alpha-tech` absent.

## Health Checks

- API:
  - `GET /api/v1/health`
- Core API smoke:
  - `GET /api/v1/ipo/pipeline`
  - `GET /api/v1/ipo/pipeline?refresh=true&corp_code=00126380`
  - `GET /api/v1/company/snapshot?corp_code=00126380`
  - `GET /api/v1/quality/summary`
  - `GET /api/v1/quality/overview`
  - `GET /api/v1/quality/rules`
  - `GET /api/v1/quality/issues`

## Data Quality Operations

- Issue query:
  - `GET /api/v1/quality/issues?source=DART&severity=FAIL`
- Rule dictionary query:
  - `GET /api/v1/quality/rules`
  - `GET /api/v1/quality/rules?source=KRX&severity=FAIL`
- Entity history:
  - `GET /api/v1/quality/entity/00126380`
- Summary trend:
  - `GET /api/v1/quality/summary?from=2026-02-01&to=2026-02-14`

- Severity policy:
  - `PASS`: publish
  - `WARN`: publish + log issue
  - `FAIL`: block publish, keep previous snapshot

## Incident Handling

1. Source outage (DART/KIND/KRX):
   - Confirm `source_status` and `partial` fields in API responses.
   - Check request logs and retry counts.
   - For KRX `LOGOUT`/`403` responses, verify endpoint access policy and session constraints for current runtime network.
   - For KRX Open API `401 Unauthorized Key` or `Unauthorized API Call`, verify both:
     - API key issuance status in Open API portal
     - Per-service usage approval (API application) for the target API
   - For KRX Open API `404 API referenced by the path does not exist`, fix `KRX_API_*_PATH` from portal sample URL.
2. Schema drift:
   - Validate KRX dataset registry `bld` values and sample schema.
3. Empty data:
   - Re-run ETL for the impacted date window.
   - Verify connector-level raw payload capture.
4. Quality gate blocks publish:
   - Check `snapshot_publish_log` entries with `published=false`.
   - Query `data_quality_issue` by `batch_id` and `severity=FAIL`.

## KRX Connectivity Check

- Quick probe:
  - `cd backend`
  - `python scripts/krx_openapi_probe.py`
  - probe reads all configured KRX category paths from root `.env`.
  - success criterion: strict category has at least one `OK` path.

- Repeat probe for stability:
  - `python scripts/krx_openapi_probe.py --repeat 5 --bas-dd 20250131 --strict-categories stock,esg`
  - Use `--strict-categories` to control pass/fail gate categories.

- Current validated baseline (2026-02-16):
  - `index`, `stock`, `securities`, `bond`, `derivative`, `general`: `OK`
  - `esg`: `partial` (`esg/sri_bond_info` OK, `esg/esg_index_info` and `esg/esg_etp_info` require usage approval)
  - runtime refresh path includes transient retry for intermittent KRX `403 Access Denied`.
  - refresh response includes `source_status_detail` (path-level status/rows/attempts/error).

## One-shot ETL Execution

- `cd backend`
- `python scripts/run_pipeline_once.py --corp-code 00126380`
- Then check:
  - `GET /api/v1/quality/issues`
  - `GET /api/v1/quality/summary`

## Recovery Checklist

1. Confirm DB connectivity.
2. Confirm API `/health`.
3. Re-run backend tests:
   - `cd backend && python -m pytest -q`
4. Re-run web e2e:
   - `cd web && npx playwright test`
5. Re-run web build with cleanup:
   - `cd web && npm run build:stable`
   - `build:stable` clears `.next*` artifacts before build and is the default recovery command.

## Web Build Stability Notes

- `next.config.ts` splits output directories by mode:
  - production: `.next-build`
  - development: `.next-dev`
- UI fonts run on local CSS stacks (`web/app/globals.css`) and do not use `next/font/google`.
- Do not run parallel `next build` and Playwright in the same workspace during incident triage.
