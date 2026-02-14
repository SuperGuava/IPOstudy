# Data Quality Hardening Design (Phase 1)

**Date:** 2026-02-14  
**Status:** Approved

## 1) Goal
- Improve operational data quality for DART, KIND, and KRX ingestion paths.
- Prevent bad data from being published to snapshots while preserving service continuity.
- Provide operators with quality visibility through logs and summary APIs.

## 2) Scope
- In-scope:
  - Rules-based quality checks for DART/KIND/KRX and cross-source consistency.
  - Quality gate before snapshot publish (`PASS`, `WARN`, `FAIL`).
  - Quality issue storage, daily summary storage, and quality query APIs.
- Out-of-scope:
  - ML/anomaly scoring.
  - Full observability stack redesign.
  - Security/performance/CI-CD hardening (scheduled for later phases).

## 3) Architecture Changes
- Existing pipeline:
  - `raw_ingest -> normalize -> reconcile -> snapshot publish`
- Updated pipeline:
  - `raw_ingest -> normalize -> reconcile -> quality_gate -> snapshot publish`
- Publish policy:
  - `PASS`: publish immediately.
  - `WARN`: publish with issue logs.
  - `FAIL`: block publish and keep previous snapshot.

## 4) Quality Rule Set

### 4.1 Common
- Required key presence checks:
  - `corp_code`, `pipeline_id`, `rcept_no`, `dataset_key` (where applicable)
- Date format checks:
  - `YYYYMMDD` or `YYYY-MM-DD`
- Numeric value checks:
  - type validity, forbidden negatives

### 4.2 DART
- `rcept_no` format validation.
- Latest-report consistency preference (`last_reprt_at=Y`).
- `corp_code` existence and mapping validity.
- `estkRs` core fields non-empty checks.

### 4.3 KIND
- Stage value must be one of:
  - `예비심사`, `공모`, `상장예정`, `신규상장`
- At least one key date present.
- Duplicate row detection by normalized identity.

### 4.4 KRX
- Dataset registry required params must be satisfied.
- Response minimum key checks (`OutBlock_1` etc.).
- Empty-day detection (`0 records`) for expected windows.
- Symbol format and optional cross-check with DART stock code.

### 4.5 Cross-Source
- KIND IPO candidates vs DART filing linkage ratio threshold.
- Post-listing KRX attachment success ratio threshold.
- Threshold breach mapped to `WARN` or `FAIL`.

## 5) Data Model Additions
- `data_quality_issue`
  - `id`, `source`, `rule_code`, `severity`, `entity_type`, `entity_key`, `message`, `observed_at`, `batch_id`
- `data_quality_summary_daily`
  - `summary_date`, `source`, `pass_count`, `warn_count`, `fail_count`, `fail_rate`
- `snapshot_publish_log`
  - `snapshot_type`, `entity_key`, `published`, `blocked_reason`, `batch_id`, `published_at`

## 6) API Additions
- `GET /api/v1/quality/issues`
  - filters: `source`, `severity`, `from`, `to`, `rule_code`
- `GET /api/v1/quality/summary`
  - daily/source summary metrics
- `GET /api/v1/quality/entity/{entity_key}`
  - issue history for one entity

## 7) Error Handling
- Rule execution errors are recorded as `FAIL` issues with rule-level context.
- On quality gate `FAIL`, API data remains from last successful snapshot.
- Quality API always returns deterministic output even if no issues exist.

## 8) Testing Strategy
- Unit:
  - Rule evaluators by source.
- Integration:
  - `FAIL` data blocks snapshot publish.
  - `WARN` data publishes with issue logs.
- API:
  - filter and schema behavior for quality endpoints.
- Regression:
  - existing APIs remain functional after gate insertion.

## 9) Rollout Strategy
- Stage 1:
  - Enable quality checks and logging only.
- Stage 2:
  - Enable blocking for selected `FAIL` rules.
- Stage 3:
  - Tune thresholds using operational trends.

