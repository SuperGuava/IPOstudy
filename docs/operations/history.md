# Execution History and Major Notes

Updated: 2026-02-18 09:45 (+09:00)

## 1) Repository / Integration History

- Main repository: `https://github.com/SuperGuava/IPOstudy.git`
- Default branch: `main`
- Merged PR: `#1` (feature work integrated into `main`)
- Current `main` head: `e19022c` (`security: redact db password example from operations history`)

Recent milestone commits:

1. `6135379` `feat: add data quality persistence schema`
2. `dd42d56` `feat: add common data quality rule engine`
3. `b23c7b6` `feat: add source-specific and cross-source quality rules`
4. `ad66e32` `feat: integrate quality gate into snapshot publish flow`
5. `f39f104` `feat: add quality reporting APIs`
6. `ddefa05` `feat: add daily data quality summary job`
7. `4454fa2` `test: add quality gate end-to-end regression coverage`
8. `a14d6be` `docs: add data quality operations and API references`

## 2) Runtime Decisions (Execution First)

- Local DB target: PostgreSQL (Docker)
- Local cache target: Redis (Docker)
- PostgreSQL host port: `55432` (changed from `5432` to avoid local port conflict)
- App DB connection convention:
  - `postgresql+psycopg://<db_user>:<db_password>@localhost:55432/anti_gravity`

Files currently reflecting runtime decision:

- `infra/docker-compose.yml`
- `backend/alembic.ini`
- `.env.example`

## 3) Current Runtime Verification (2026-02-15)

Infra / migration:

1. `docker compose -f infra/docker-compose.yml up -d` -> `postgres`, `redis` running
2. `cd backend && python -m alembic upgrade head` -> success on `PostgresqlImpl`

Backend / web:

1. `GET /api/v1/health` -> `{"status":"ok"}`
2. `GET /api/v1/ipo/pipeline` -> `200`, sample item returned
3. `GET /api/v1/company/snapshot?corp_code=00126380` -> `200`
4. `GET /api/v1/quality/issues` -> `200`, `{"items":[],"total":0}`
5. `GET /api/v1/quality/summary` -> `200`, `{"items":[],"total":0}`
6. `GET /api/v1/export/ipo.xlsx` -> `200`, xlsx content-type
7. `GET /api/v1/export/company/00126380.xlsx` -> `200`, xlsx content-type
8. Web root `http://127.0.0.1:3000` -> `200`

Tests:

1. `cd backend && python -m pytest -q` -> `45 passed`
2. `cd web && npm test -- --runInBand` -> placeholder script output (no unit suite yet)
3. `cd web && npx playwright test` -> `1 passed`

## 4) Working Tree Notes

- Branch: `main`
- Untracked file intentionally preserved: `guava_guide.md`
- No destructive reset/checkout used

## 5) Next Execution Roadmap (Step-by-step)

1. **Data fill run**: completed (`backend/scripts/run_pipeline_once.py`)
2. **Execution scripts**: in progress (next: add start/smoke/stop wrapper)
3. **Feature iteration 1**: completed (IPO API now DB-backed with optional live refresh)
4. **Design iteration 1**: next, improve dashboard UX/layout with existing API contracts.

## 6) External Source Connectivity Snapshot

Direct connector probes (2026-02-15):

1. DART `company.json` (`corp_code=00126380`) -> success (`status=000`)
2. KIND public offering page parse -> request success, parsed rows `0` in current environment
3. KRX dataset endpoint (`getJsonData.cmd`) -> blocked response (`HTTP 400`, body `LOGOUT`)

KRX debugging notes:

- Simple POST: `403 Forbidden`
- Browser-like headers applied: `403` to `400(LOGOUT)` shifted
- Session preflight added (`mdiLoader/index.cmd`) + cookie-enabled client: still `400(LOGOUT)`
- Official KRX Open API flow implemented (`AUTH_KEY` + `GET https://data-dbg.krx.co.kr/svc/apis/...`)
- Live probe with current key result: `401 Unauthorized Key`
- Current conclusion: runtime is now aligned to official KRX Open API pattern; remaining blocker is key/service authorization state in KRX portal.

Implementation notes (2026-02-15):

1. Added KRX Open API client path in connector:
   - `fetch_open_api(api_path, params)` with `AUTH_KEY` header
   - auth error mapping: `KrxAuthError`
2. Added connector tests for Open API header/path/auth failure mapping.
3. Added probe script:
   - `backend/scripts/krx_openapi_probe.py`

## 7) Live ETL One-shot Execution (2026-02-15)

Command:

- `cd backend && python scripts/run_pipeline_once.py --corp-code 00126380`

Observed output:

1. `pipeline_batch_id=live-20260215095717`
2. `published=False`
3. `kind_rows=0`, `dart_rows=0`
4. `krx_status=auth_error:Unauthorized Key`
5. `issues_total=1` (`FAIL=1`)
6. `daily_summary_sources=1`

DB verification:

1. `data_quality_issue` count: `1`
2. `data_quality_summary_daily` count: `1`
3. latest issue: `KRX_RESPONSE_SCHEMA / FAIL / batch_id=live-20260215095717`

API verification after backend restart with `.env`:

1. `GET /api/v1/quality/issues` -> `total=1`
2. `GET /api/v1/quality/summary` -> `total=1`

## 8) Feature Iteration 1 Completion (2026-02-15)

Implemented:

1. Replaced static IPO API payload with DB-backed read path.
2. Added missing-detail handling: `/api/v1/ipo/{pipeline_id}` returns `404` when not found.
3. Added optional live refresh path:
   - `GET /api/v1/ipo/pipeline?refresh=true&corp_code=...&bas_dd=...`
   - pulls DART/KIND + configured KRX category APIs, then runs ETL pipeline.
4. Added KRX multi-category expansion env keys:
   - `KRX_API_INDEX_PATH`, `KRX_API_STOCK_PATH`, `KRX_API_SECURITIES_PATH`, `KRX_API_BOND_PATH`, `KRX_API_DERIVATIVE_PATH`, `KRX_API_GENERAL_PATH`, `KRX_API_ESG_PATH`

Verification:

1. `cd backend && python -m pytest -q` -> `46 passed`
2. `GET /api/v1/ipo/pipeline` -> DB item response (`total=1`)
3. `GET /api/v1/ipo/__missing_pipeline_id__` -> `404`
4. `GET /api/v1/ipo/pipeline?refresh=true&corp_code=00126380` -> refresh metadata included

## 9) Productization Phase 4 (UI/UX) Execution (2026-02-15)

Implemented:

1. Tailwind dark theme foundation and global design tokens.
2. Product shell:
   - left navigation (`Dashboard`, `IPO Pipeline`, `Company Snapshot`, `Quality`, `Export`)
   - top header structure
3. IPO surface:
   - KPI strip
   - stage distribution strip
   - dense data grid
   - detail drawer with source status badges
4. Frontend API integration:
   - `web/lib/api.ts` switched from static fixtures to backend API fetches
   - `/ipo` supports refresh query workflow
5. Added placeholder pages for `Quality` and `Export` modules under shell.

Verification:

1. `cd backend && python -m pytest -q` -> `46 passed`
2. `cd web && npm test -- --runInBand` -> placeholder script output
3. `cd web && npx playwright test tests/e2e/ipo-flow.spec.ts` -> `1 passed`
4. `cd web && npm run build` -> success

## 10) Dashboard + Quality Productization Follow-up (2026-02-15)

Implemented:

1. `Dashboard` now uses live API data:
   - pipeline size, offering count, latest fail-rate, issue backlog
   - pipeline feed + recent issues panel
2. `Quality` now uses live API data:
   - issue total / fail / warn metrics
   - issue feed table + daily summary panel
3. E2E regression expanded:
   - dashboard metrics visible check
   - quality page issue feed visible check

Verification:

1. `cd backend && python -m pytest -q` -> `46 passed`
2. `cd web && npm test -- --runInBand` -> placeholder script output
3. `cd web && npx playwright test` -> `2 passed`
4. `cd web && npm run build` -> success (single run)

Note:

- During one parallel verification run, `next build` intermittently reported `PageNotFoundError: /_document`.
- Immediate single re-run completed successfully.

## 11) Quality Filters + Dashboard Trend Iteration (2026-02-15)

Implemented:

1. Dashboard:
   - added `Stage Mix` distribution bars
   - added `Fail Rate Trend` bars from quality summary history
2. Quality:
   - added filter form (`source`, `severity`, `from`, `to`)
   - filter state propagated to both issue feed and summary panels
3. API client:
   - added filter query support in `getQualityIssues` and `getQualitySummary`

Verification:

1. `cd backend && python -m pytest -q` -> `46 passed`
2. `cd web && npm test -- --runInBand` -> placeholder script output
3. `cd web && npx playwright test` -> `2 passed`
4. `GET /api/v1/quality/issues?severity=FAIL` -> `200`
5. `GET /api/v1/quality/summary?source=KRX` -> `200`
6. `cd web && npm run build` -> success (single run)

## 12) Web Build Stability Hardening (2026-02-16)

Root-cause observations:

1. `next build` intermittently failed with `PageNotFoundError: /_document` when concurrent build/e2e runs overlapped.
2. Build logs showed repeated external font fetch retries from `next/font/google`, adding network volatility.

Implemented:

1. Build output isolation by mode (`web/next.config.ts`):
   - production: `.next-build`
   - development: `.next-dev`
   - optional override: `NEXT_DIST_DIR`
2. Added stable build scripts (`web/package.json`):
   - `build:clean` (clear `.next-build`, `.next-dev`, `.next`)
   - `build:stable` (clean + build)
3. Removed `next/font/google` dependency from root layout and switched to local CSS font stacks (`web/app/globals.css`).

Verification (2026-02-16):

1. `cd web && npm run build:stable` -> success
2. `cd web && npm run build` repeated 3 times -> all success
3. No font download/network retry patterns found in repeated build logs
4. `cd web && npx playwright test` -> `2 passed`

## 13) KRX Key Rotation Check (2026-02-16)

Applied:

1. Rotated runtime `KRX_API_KEY` in root `.env` to the newly provided key.

Verification:

1. `cd backend && python scripts/krx_openapi_probe.py` -> `KRX Open API AUTH ERROR: Unauthorized API Call`
2. `cd backend && python scripts/run_pipeline_once.py --corp-code 00126380` ->
   - `krx_status=auth_error:Unauthorized API Call`
   - pipeline publish blocked by quality gate (`FAIL=1`)

Conclusion:

1. Runtime integration path is healthy, but KRX portal-side API usage approval for the target service path is still required.

## 14) KRX Approval Activation + Path Remap (2026-02-16)

Observed:

1. New key remained `401 Unauthorized API Call` for `sto/stk_isu_base_info`.
2. Direct matrix probe showed many APIs already authorized and returning `200`.

Applied:

1. Updated runtime `.env` KRX category paths to authorized endpoints:
   - `index=idx/krx_dd_trd`
   - `stock=sto/stk_bydd_trd`
   - `securities=sto/ksq_bydd_trd`
   - `bond=bon/bnd_bydd_trd`
   - `derivative=drv/opt_bydd_trd`
2. Updated `.env.example` defaults to same validated paths.
3. Fixed script hardcoding:
   - `backend/scripts/krx_openapi_probe.py` now resolves `KRX_API_STOCK_PATH`
   - `backend/scripts/run_pipeline_once.py` now resolves `KRX_API_STOCK_PATH`
4. Added regression tests:
   - `backend/tests/scripts/test_krx_script_paths.py`

Verification:

1. `cd backend && python -m pytest -q` -> `50 passed`
2. `cd backend && python scripts/krx_openapi_probe.py` ->
   - `KRX Open API OK: path=sto/stk_bydd_trd rows=961`
3. `cd backend && python scripts/run_pipeline_once.py --corp-code 00126380 --bas-dd 20250131` ->
   - `published=True`, `issues_total=0`, `krx_status=ok`
4. `GET /api/v1/ipo/pipeline?refresh=true&corp_code=00126380&bas_dd=20250131` ->
   - `published=True`, `krx_rows=5`

## 15) KRX Multi-category Probe Upgrade (2026-02-16)

Observed:

1. KRX Open API portal pages were intermittently blocked (`403` / service unavailable) in this runtime, so direct catalog scraping for `general/esg` path discovery was not reliable.
2. Candidate path probe for `general/esg` returned `404 API referenced by the path does not exist` for tested guesses.

Applied:

1. Expanded `backend/scripts/krx_openapi_probe.py`:
   - now resolves all category paths from `.env`
   - probes each category and prints `OK/SKIP/AUTH ERROR/ERROR` with category and path
   - exit code now gates primarily on `stock` category success
2. Added script regression tests:
   - `backend/tests/scripts/test_krx_script_paths.py` expanded with `resolve_probe_paths` coverage.
3. Updated runbook guidance for:
   - full-category probe behavior
   - handling `404` invalid path errors
   - current baseline (`general/esg` not configured)

Verification:

1. `cd backend && python -m pytest -q` -> `52 passed`
2. `cd backend && python scripts/krx_openapi_probe.py` ->
   - `index/stock/securities/bond/derivative: OK`
   - `general/esg: SKIP (not_configured)`

## 16) KRX Multi-path Category Expansion (2026-02-16)

Observed:

1. KRX key had multiple approved endpoints, but single-path category config underused available data sources.
2. `ipo_service.refresh_pipeline_live` read env paths once at import and could not consume comma-separated path sets.

Applied:

1. Added runtime path resolver in `backend/app/services/ipo_service.py`:
   - `resolve_krx_openapi_paths(env)` with comma-separated parsing
   - category-wise multi-path calls with aggregated status (`ok`, `partial`, `auth_error`, etc.)
2. Added service tests:
   - `backend/tests/services/test_ipo_service.py`
3. Upgraded probe script for multi-path category probing:
   - `backend/scripts/krx_openapi_probe.py`
4. Expanded script tests:
   - `backend/tests/scripts/test_krx_script_paths.py`
5. Updated environment templates to validated multi-path defaults:
   - `index=idx/krx_dd_trd,idx/kospi_dd_trd,idx/kosdaq_dd_trd`
   - `stock=sto/stk_bydd_trd`
   - `securities=sto/ksq_bydd_trd,sto/ksq_isu_base_info`
   - `bond=bon/bnd_bydd_trd`
   - `derivative=drv/fut_bydd_trd,drv/opt_bydd_trd`
   - `general=sto/knx_bydd_trd,sto/knx_isu_base_info`
   - `esg=` (pending valid path)

Verification:

1. `cd backend && python -m pytest -q` -> `55 passed`
2. `cd backend && python scripts/krx_openapi_probe.py` ->
   - `index/stock/securities/bond/derivative/general: OK`
   - `esg: SKIP (not_configured)`
3. `GET /api/v1/ipo/pipeline?refresh=true&corp_code=00126380&bas_dd=20250131` ->
   - `published=True`, `krx_rows=11`
   - `source_status.general=ok:244`, `source_status.esg=not_configured`
4. `cd backend && python scripts/run_pipeline_once.py --corp-code 00126380 --bas-dd 20250131` ->
   - `published=True`, `issues_total=0`, `krx_status=ok`

## 17) ESG Path Activation (2026-02-16)

Observed:

1. After ESG service application, the following paths were verified:
   - `esg/sri_bond_info` -> `200` with expected bond fields
   - `esg/esg_index_info` -> `401 Unauthorized API Call` (path exists; approval pending)
2. Automated endpoint guess for ESG securities product path did not find an additional `200` path in this runtime.

Applied:

1. Updated root `.env`:
   - `KRX_API_ESG_PATH=esg/sri_bond_info,esg/esg_index_info`
2. Updated `.env.example` with same ESG defaults.

Verification:

1. `GET /api/v1/ipo/pipeline?refresh=true&corp_code=00126380&bas_dd=20250131` ->
   - `status=200`
   - `published=True`
   - `source_status.esg=partial:ok=2262,auth=1,schema=0,error=0`
2. direct probe:
   - `GET /svc/apis/esg/sri_bond_info` -> `200`
   - `GET /svc/apis/esg/esg_index_info` -> `401`

## 18) KRX Access Denied Retry Stabilization (2026-02-16)

Observed:

1. KRX Open API intermittently returned WAF-style `403 Access Denied` for otherwise valid paths.
2. This caused occasional `auth_error` noise in refresh status even when the same path succeeded on retry.

Applied:

1. Added transient retry logic in `backend/app/services/ipo_service.py`:
   - `_fetch_krx_with_retry(...)`
   - retries up to 3 times only for `KrxAuthError` containing `Access Denied`
2. Added regression coverage:
   - `backend/tests/services/test_ipo_service.py::test_refresh_pipeline_live_retries_transient_access_denied`

Verification:

1. `cd backend && python -m pytest -q` -> `56 passed`
2. Repeated refresh checks (`x3`) with `bas_dd=20250131`:
   - all returned `status=200`, `published=True`
   - stable ESG status: `partial:ok=2262,auth=1,schema=0,error=0`

## 19) ESG ETP Path Registration (2026-02-16)

Input:

1. User provided KRX API ID: `esg_etp_info` (ESG securities product).

Applied:

1. Updated ESG path configuration:
   - `.env` and `.env.example`
   - `KRX_API_ESG_PATH=esg/sri_bond_info,esg/esg_index_info,esg/esg_etp_info`

Verification:

1. `cd backend && python scripts/krx_openapi_probe.py` ->
   - `esg/sri_bond_info` -> `OK`
   - `esg/esg_index_info` -> `AUTH ERROR`
   - `esg/esg_etp_info` -> `AUTH ERROR`
2. `GET /api/v1/ipo/pipeline?refresh=true&corp_code=00126380&bas_dd=20250131` ->
   - `status=200`, `published=True`
   - `source_status.esg=partial:ok=2262,auth=2,schema=0,error=0`

Note:

1. Provided sample key from the API spec page returned `401` for live `/svc/apis` calls; runtime key remains the active key.

## 20) Cross-session Handoff Packaging (2026-02-16)

Applied:

1. Rewrote `guava_guide.md` to current productization/operations baseline.
2. Added `docs/operations/session-handoff.md` with bootstrap/run/smoke/next-task checklist.
3. Linked handoff docs from `README.md` and `docs/operations/runbook.md`.
4. Extended `.gitignore` for local web artifacts:
   - `.next-build`, `.next-dev`, `web/build_*.log`, `web/pw_*.log`

Intent:

1. New session can resume development without prior chat context.
2. Reduce accidental commit noise from local build artifacts.

## 21) Sprint 1 Completion - ESG/KRX Verification Hardening (2026-02-17)

Applied:

1. Upgraded `backend/scripts/krx_openapi_probe.py` with:
   - `--repeat`
   - `--bas-dd`
   - `--strict-categories`
2. Added probe helper tests:
   - strict category parser
   - category success predicate
3. Added refresh path-level diagnostics:
   - `source_status_detail` in `/api/v1/ipo/pipeline?refresh=true...`
   - fields: `path`, `status`, `rows`, `attempts`, optional `error`

Verification:

1. `cd backend && python scripts/krx_openapi_probe.py --repeat 5 --bas-dd 20250131 --strict-categories stock,esg`
2. Refresh API repeated 5 times:
   - all runs `status=200`, `published=True`
   - ESG remained partial (`ok + auth_pending`) as expected.

## 22) Sprint 2 Completion - Data Quality Rule Expansion (2026-02-17)

Applied:

1. Expanded KRX quality rules in `backend/app/quality/rules/krx.py`:
   - `KRX_BAS_DD_MISMATCH` (WARN)
   - `KRX_DUPLICATE_ISU_CD` (WARN)
   - `KRX_NUMERIC_FIELD_INVALID` (WARN)
2. Added aggregate endpoint:
   - `GET /api/v1/quality/overview`
3. Upgraded quality UI:
   - source breakdown panel
   - top rule codes panel

Verification:

1. `python -m pytest tests/quality/test_krx_rules.py -q` -> pass
2. `python -m pytest tests/api/test_quality_api.py -q` -> pass

## 23) Sprint 3 Completion - Collection Stability and Performance (2026-02-17)

Applied:

1. Added connector-level auth taxonomy:
   - `KrxAccessDeniedError` (403 Access Denied)
   - `KrxAuthError` for auth/approval errors
2. Retry policy upgrade in `ipo_service`:
   - retry only `KrxAccessDeniedError` and request errors
   - no retry for `Unauthorized API Call`
3. Parallelized KRX path fetch in refresh flow:
   - ThreadPool-based concurrent path collection

Verification:

1. `python -m pytest -q` -> `65 passed`
2. `cd web && npx playwright test` -> `2 passed`
3. `cd web && npm run build:stable` -> success

## 24) KIND Full Listing Recovery + Snapshot Replace Fix (2026-02-17)

Observed:

1. `/api/v1/ipo/pipeline` showed only one demo company in some environments.
2. KIND main page (`searchPubofrProgComMain`) returned HTML shell, but row data was loaded via server-side sub request.
3. Existing publish path used merge/upsert and could leave old demo rows after live refresh.

Applied:

1. `backend/app/connectors/http_client.py`
   - added `post_text(...)` helper for form-post HTML fetch.
2. `backend/app/connectors/kind_connector.py`
   - switched to `searchPubofrProgComSub` POST fetch path
   - added robust parser for modern/legacy table structures
   - normalized stage values to quality-compatible set (`prelisting`, `listed`, fallback `offering`)
3. `backend/app/etl/pipeline.py`
   - publish path now replaces old snapshot rows (`delete(IpoPipelineItem)` before insert loop)
4. Tests updated:
   - `backend/tests/connectors/test_kind_connector.py`
   - `backend/tests/etl/test_pipeline_e2e.py`
   - new fixture `backend/tests/fixtures/kind/pubofrprogcom_sub.html`

Verification:

1. `cd backend && python -m pytest -q` -> `67 passed`
2. `GET /api/v1/ipo/pipeline?refresh=true&corp_code=00126380&bas_dd=20250131` ->
   - `status=200`
   - `refresh.published=true`
   - `refresh.kind_rows=2301`
3. `GET /api/v1/ipo/pipeline` ->
   - `total=2301`
   - demo row (`alpha-tech`) absent

## 25) Quality Rule Catalog for Non-experts (2026-02-17)

Applied:

1. Added quality rule dictionary module:
   - `backend/app/quality/catalog.py`
2. Added API endpoint:
   - `GET /api/v1/quality/rules`
   - optional filters: `source`, `severity`
3. Expanded quality page UX:
   - issue feed now shows `rule_code` + human-readable title
   - top rule panel now shows title next to code
   - added `Rule Guide (Beginner)` panel with plain-language description and operator action
4. Updated operations docs:
   - `README.md`, `guava_guide.md`, `docs/operations/runbook.md`, `docs/operations/session-handoff.md`

Verification:

1. `cd backend && python -m pytest -q tests/api/test_quality_api.py` -> pass
2. `cd backend && python -m pytest -q` -> pass
3. `cd web && npm run build:stable` -> pass

## 26) Company Explorer Foundation (Beyond IPO, 2026-02-17)

Applied:

1. Added insights API surface:
   - `GET /api/v1/insights/companies` (search/list)
   - `GET /api/v1/insights/company` (beginner summary + quality snapshot)
   - `GET /api/v1/insights/templates` (analysis templates)
2. Added backend composition service:
   - `backend/app/services/insight_service.py`
   - company risk label (`low|medium|high`) from quality severity counts
3. Added web explorer UX:
   - `web/app/explorer/page.tsx`
   - beginner summary, quick insights, quality snapshot, analysis templates
   - left-side search/list + right-side detail pattern
4. Added navigation and e2e coverage:
   - `web/components/app-shell.tsx`
   - `web/tests/e2e/ipo-flow.spec.ts`
5. Updated operations docs (`README.md`, runbook, handoff, guide).

Verification:

1. `cd backend && python -m pytest -q` -> pass
2. `cd web && npm run build:stable` -> pass
3. `cd web && npx playwright test` -> pass

## 27) Explorer Upgrade: Filters, Compare, Guided Report (2026-02-17)

Applied:

1. Extended insights API:
   - `GET /api/v1/insights/companies` now supports `stage`, `risk_label`
   - `GET /api/v1/insights/compare` for multi-company side-by-side summary
   - `GET /api/v1/insights/report` for template-based beginner report lines
2. Extended backend service:
   - risk-aware company filtering
   - compare summary (`max_fail`, `avg_warn`, `risk_distribution`)
   - template-based report generation (`foundation-check`, `quality-risk-scan`, `listing-readiness`)
3. Upgraded Explorer UX:
   - stage/risk/template controls
   - per-row compare toggle (`Add Compare` / `Remove Compare`)
   - `Beginner Report` panel
   - `Compare Snapshot` panel
4. Updated docs for new API and smoke flow.

Verification:

1. `cd backend && python -m pytest -q tests/api/test_insights_api.py` -> `6 passed`
2. `cd backend && python -m pytest -q` -> `75 passed`
3. `cd web && npm run build:stable` -> pass
4. `cd web && npx playwright test` -> `3 passed`
5. Runtime check:
   - `GET /api/v1/insights/companies?limit=5` -> `200`
   - `GET /api/v1/insights/company?company_key=name:3R` -> `200`
   - `GET /api/v1/insights/compare?company_key=name:3R&company_key=name:3S` -> `200`
   - `GET /api/v1/insights/report?company_key=name:3R&template_id=foundation-check` -> `200`

## 28) Explorer Overview KPI Layer (2026-02-17)

Applied:

1. Added insights overview API:
   - `GET /api/v1/insights/overview`
   - aggregates: `total_companies`, `stage_counts`, `risk_counts`, `top_lead_managers`
2. Added backend test coverage:
   - `test_insight_overview_returns_aggregates`
3. Upgraded Explorer page:
   - top KPI cards (`Total Companies`, `Listed`, `Prelisting`, `High Risk`)
   - `Top Lead Managers` panel
4. Updated operations and guide docs with new endpoint.

Verification:

1. `cd backend && python -m pytest -q tests/api/test_insights_api.py` -> `7 passed`
2. `cd backend && python -m pytest -q` -> `76 passed`
3. `cd web && npm run build:stable` -> pass
4. `cd web && npx playwright test` -> `3 passed`

## 29) Deployment Readiness and Docker Production Stack (2026-02-17)

Applied:

1. Added backend containerization:
   - `backend/Dockerfile`
   - `backend/.dockerignore`
2. Added web containerization:
   - `web/Dockerfile`
   - `web/.dockerignore`
3. Added production compose stack:
   - `infra/docker-compose.prod.yml`
   - services: `postgres`, `redis`, `backend`, `web`
   - backend startup includes migration (`alembic upgrade head`)
   - healthchecks for db/cache/api/web
4. Migration config hardening:
   - `backend/alembic/env.py` now respects runtime `DATABASE_URL`
5. Runtime dependency fix:
   - added `psycopg[binary]` in `backend/pyproject.toml`
6. Web API base hardening:
   - `web/lib/api.ts` now prefers `API_BASE_URL` over `NEXT_PUBLIC_API_BASE_URL`
7. Added deployment docs:
   - `docs/operations/deployment.md`
   - updated `README.md`, runbook, handoff, guide

Verification:

1. `cd backend && python -m pytest -q` -> `76 passed`
2. `cd web && npx playwright test` -> `3 passed`
3. `cd web && npm run build:stable` -> pass
4. `docker compose -f infra/docker-compose.prod.yml config` -> valid
5. `docker compose -f infra/docker-compose.prod.yml up -d --build` -> stack healthy
6. Runtime smoke on deployed stack:
   - `GET /api/v1/health` -> `200`
   - `GET /api/v1/insights/overview` -> `200`
   - `GET /api/v1/insights/companies?limit=2` -> `200`
   - `GET /` on web (`3000`) -> `200`

## 30) Plan A Public Deploy Preparation (Vercel + Render, 2026-02-17)

Observed:

1. Vercel CLI auth was missing in current environment:
   - `npx vercel whoami` -> no credentials
2. Without Vercel login/token, direct web publish cannot complete from this session.

Applied:

1. Added Render blueprint:
   - `render.yaml`
   - web service (`backend` Docker), managed Postgres, managed Redis
2. Added DB URL normalization for managed platforms:
   - `backend/app/db/url.py`
   - used by `backend/app/db/session.py`
   - used by `backend/alembic/env.py`
3. Hardened backend Docker startup for managed deployment:
   - `backend/Dockerfile` now runs migration before uvicorn
4. Added launch validation API:
   - `GET /api/v1/insights/validation`
   - includes approval conditions, kill criteria, and budget model
5. Upgraded Explorer UI:
   - added `Validation Gate` panel
6. Added deployment runbook:
   - `docs/operations/vercel-render-deploy.md`
   - linked from README/runbook/handoff

Verification:

1. `cd backend && python -m pytest -q tests/api/test_insights_api.py` -> `8 passed`
2. `cd backend && python -m pytest -q` -> `77 passed`
3. `cd web && npx playwright test` -> `3 passed`

## 31) Resume Verification Pass (2026-02-17)

Observed:

1. Session resumed with uncommitted deploy/readme updates and a pending "ESG approval re-check + repeat verification" task from handoff.
2. Local infra bootstrap required explicit `POSTGRES_PASSWORD` at compose runtime in this shell.
3. `web` build showed `spawn EPERM` in restricted execution mode, but this was environmental (permission scope), not app code regression.

Applied:

1. Rebootstrapped local infra (`postgres`, `redis`) and re-ran pipeline checks.
2. Re-verified backend test suite and KRX strict probes.
3. Re-ran live refresh loop (`run_pipeline_once.py`) five times with fixed inputs.
4. Updated handoff references to latest verified numbers and current pending actions.

Verification:

1. `cd backend && python -m pytest -q` -> `80 passed`
2. `cd backend && python scripts/krx_openapi_probe.py --repeat 5 --bas-dd 20250131 --strict-categories stock,esg` ->
   - all iterations: `stock=OK`
   - all iterations: `esg` remained `partial` (`esg_index_info`, `esg_etp_info` auth pending)
3. `cd backend && python scripts/run_pipeline_once.py --corp-code 00126380 --bas-dd 20250131` repeated 5 times ->
   - all runs `published=True`
   - all runs `kind_rows=2301`, `dart_rows=20`, `krx_status=ok`
4. `cd web && npm run build:stable` -> pass in full-permission shell (restricted shell may show `spawn EPERM`)

## 32) API Refresh Verification Alignment (2026-02-17)

Observed:

1. `:8000` API refresh returned `source_status.*=missing_key` while script probes showed 정상 수집.
2. Root cause was an orphan `infra-backend-1` container running with empty `DART_API_KEY` / `KRX_API_KEY`.

Applied:

1. Re-validated KRX strict probe via script (repo root `.env` load path).
2. Started local backend (`uvicorn`) with `.env` loaded on `127.0.0.1:8010`.
3. Re-ran refresh API loop (`x5`) against the local backend process.
4. Updated handoff notes to distinguish stale container responses from true refresh behavior.

Verification:

1. `python scripts/krx_openapi_probe.py --repeat 5 --bas-dd 20250131 --strict-categories stock,esg` ->
   - `stock`: all `OK`
   - `esg`: `partial` (`esg/sri_bond_info=OK`, `esg/esg_index_info=AUTH ERROR`, `esg/esg_etp_info=AUTH ERROR`)
2. `GET /api/v1/ipo/pipeline?refresh=true&corp_code=00126380&bas_dd=20250131` (local backend `:8010`) repeated 5 times ->
   - all runs `published=True`
   - all runs `kind_rows=2301`, `dart_rows=100`, `krx_rows=12`
   - all runs `source_status.esg=partial:ok=2262,auth=2,denied=0,schema=0,error=0`

## 33) Verification Lock Established (2026-02-18)

Applied:

1. Added persistent baseline lock document:
   - `docs/operations/verification-lock.md`
2. Recorded:
   - strict probe `x5` evidence
   - refresh loop `x5` evidence
   - lock-time git head (`e19022c`)
   - no-rerun and rerun-trigger conditions
3. Linked lock policy from:
   - `docs/operations/session-handoff.md`
   - `docs/operations/runbook.md`
   - `guava_guide.md`

Intent:

1. Future sessions should not re-run full verification loops unless lock conditions changed.
