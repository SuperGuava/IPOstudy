# Verification Lock

Updated: 2026-02-18 09:45 (+09:00)

## Purpose

Prevent repeated probe/refresh reruns across sessions when runtime conditions have not changed.

## Locked Baseline

- Git HEAD at lock time: `e19022c`
- KRX approval status:
  - `esg/sri_bond_info`: approved (`OK`)
  - `esg/esg_index_info`: pending (`Unauthorized API Call`)
  - `esg/esg_etp_info`: pending (`Unauthorized API Call`)

## Evidence Snapshot

1. Strict probe (`x5`)
   - command:
     - `cd backend && python scripts/krx_openapi_probe.py --repeat 5 --bas-dd 20250131 --strict-categories stock,esg`
   - result:
     - `stock`: all `OK`
     - `esg`: all runs `partial` (`sri_bond_info=OK`, `esg_index_info/esg_etp_info=AUTH ERROR`)
2. Refresh API (`x5`, local backend with `.env` loaded)
   - endpoint:
     - `GET http://127.0.0.1:8010/api/v1/ipo/pipeline?refresh=true&corp_code=00126380&bas_dd=20250131`
   - result:
     - all runs `published=True`
     - all runs `kind_rows=2301`, `dart_rows=100`, `krx_rows=12`
     - all runs `source_status.esg=partial:ok=2262,auth=2,denied=0,schema=0,error=0`

## No-Rerun Policy

You can skip re-running probe/refresh if all conditions below are true:

1. No code changes in:
   - `backend/app/connectors/`
   - `backend/app/services/ipo_service.py`
   - `backend/scripts/krx_openapi_probe.py`
   - `backend/scripts/run_pipeline_once.py`
2. No environment changes in:
   - root `.env` keys `DART_API_KEY`, `KRX_API_KEY`, `KRX_API_*_PATH`
3. KRX portal approval state unchanged (still pending for `esg_index_info`, `esg_etp_info`).
4. You are not validating through a stale/orphan backend container with empty keys.

## When Rerun Is Required

Rerun verification only when at least one condition below happens:

1. KRX approval status changes.
2. Any code/env path listed in No-Rerun Policy changes.
3. Runtime symptom deviates from baseline (for example, `published=False`, `kind_rows` drop, or repeated non-auth errors).

## Minimal Recheck (When Needed)

1. Run strict probe once.
2. Run refresh once on local backend with `.env` loaded.
3. Run `x5` loops only if single-run output differs from the locked baseline.
