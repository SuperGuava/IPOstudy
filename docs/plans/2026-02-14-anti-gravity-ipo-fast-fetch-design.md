# Anti-Gravity IPO Fast Fetch Design

**Date:** 2026-02-14  
**Status:** Approved

## 1) Goal
- Unify IPO pipeline and company fast snapshot into one backend API and one dashboard UI.
- Use source-of-truth channels only: DART, KIND, KRX Data Marketplace.
- Return fast responses using incremental ETL, cache, and materialized snapshots.

## 2) Scope
- Backend: FastAPI + PostgreSQL + Redis + Celery.
- Frontend: Next.js dashboard with IPO board, deal detail, company snapshot, Excel export.
- Required APIs:
  - `GET /api/v1/company/snapshot`
  - `GET /api/v1/ipo/pipeline`
  - `GET /api/v1/ipo/{pipeline_id}`
  - `GET /api/v1/company/{corp_code}/financials`
  - `GET /api/v1/export/ipo.xlsx`
  - `GET /api/v1/export/company/{corp_code}.xlsx`

## 3) Architecture
- Monolithic-by-module architecture:
  - `app/connectors` for source adapters
  - `app/etl` for raw ingest, normalize, reconcile, snapshot build
  - `app/jobs` for scheduled/incremental background jobs
  - `app/api` for serving endpoints
- Storage layers:
  - Raw store: original JSON/XML/ZIP payloads
  - Normalized store: relational canonical tables
  - Snapshot store: precomputed response-oriented tables
- Trigger model:
  - Poll DART list (`last_reprt_at=Y`)
  - If new/amended disclosure detected, refresh only affected companies/pipeline items.

## 4) Data Sources and Responsibilities
- DART:
  - Corporate master (`corp_code`, `stock_code`)
  - Company profile
  - Disclosure list and amendment tracking
  - IPO filing summary (`estkRs`)
  - Filing document ZIP
  - Financial statements and indicators
- KIND:
  - IPO stage and schedule
  - Candidate/master list for IPO pipeline
- KRX Data:
  - Post-listing market indicators (market cap, volume, turnover, investor flows)

## 5) Data Model (Minimum)
- `corp_master`
- `corp_profile`
- `dart_disclosure`
- `dart_fin_major_accounts`
- `dart_fin_full_accounts`
- `dart_fin_indicators`
- `ipo_pipeline_item`
- `ipo_pipeline_snapshot`
- `company_snapshot`
- `raw_payload_log`
- `dataset_registry`

## 6) Matching and Consistency Rules
- Stage 1 match: normalized `corp_name` + key dates.
- Stage 2 match: DART report class includes securities filing family.
- Stage 3 match: post-listing `stock_code` final reconciliation.
- Snapshot output should show only final disclosure version (`last_reprt_at=Y`), while version chains remain in normalized history.

## 7) Reliability and Error Handling
- Partial response policy:
  - API returns HTTP 200 with `partial=true` when at least one source fails.
  - Include `source_status` and `missing_sections`.
- Retry policy:
  - Retry transient (network/5xx) with exponential backoff.
  - Stop on 4xx and log source-specific reason.
- Monitoring:
  - DART/KIND/KRX health checks
  - KRX schema/hash change detection by dataset
  - Data gap alerts by market/date windows

## 8) Security
- No key hardcoding.
- Environment variables:
  - `DART_API_KEY`
  - `KRX_API_KEY`
- Mask keys in logs.
- Separate secrets per environment (dev/staging/prod).

## 9) Testing Strategy
- Unit tests:
  - Connector parsing
  - Mapping/reconcile rules
  - Snapshot assembly logic
- Integration tests:
  - Raw -> normalized -> snapshot pipeline
- API contract tests:
  - Validate OpenAPI schema and response model
- Resilience tests:
  - Single source outage still returns partial response

## 10) Approved Decisions
- Release scope: backend + full UI (including Excel export)
- Tech stack: FastAPI + PostgreSQL + Next.js
- Architecture: modular monolith

