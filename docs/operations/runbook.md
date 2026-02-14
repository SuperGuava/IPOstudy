# Operations Runbook

## Environment Variables

- `DART_API_KEY`
- `KRX_API_KEY`
- `DATABASE_URL`
- `REDIS_URL`

## Start Services

1. `docker compose -f infra/docker-compose.yml up -d`
2. Backend API:
   - `cd backend`
   - `python -m alembic upgrade head`
   - `uvicorn app.main:app --host 0.0.0.0 --port 8000`
3. Worker (future Celery integration):
   - `cd backend`
   - `python -m app.jobs.celery_app`

## Health Checks

- API:
  - `GET /api/v1/health`
- Core API smoke:
  - `GET /api/v1/ipo/pipeline`
  - `GET /api/v1/company/snapshot?corp_code=00126380`

## Incident Handling

1. Source outage (DART/KIND/KRX):
   - Confirm `source_status` and `partial` fields in API responses.
   - Check request logs and retry counts.
2. Schema drift:
   - Validate KRX dataset registry `bld` values and sample schema.
3. Empty data:
   - Re-run ETL for the impacted date window.
   - Verify connector-level raw payload capture.

## Recovery Checklist

1. Confirm DB connectivity.
2. Confirm API `/health`.
3. Re-run backend tests:
   - `cd backend && python -m pytest -q`
4. Re-run web e2e:
   - `cd web && npx playwright test`
