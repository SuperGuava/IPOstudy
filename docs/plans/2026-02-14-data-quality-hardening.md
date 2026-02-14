# Data Quality Hardening Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a rules-based quality gate for DART/KIND/KRX that logs issues, blocks invalid snapshot publish, and exposes quality reporting APIs.

**Architecture:** Insert `quality_gate` between `reconcile` and snapshot publish. Add quality persistence tables, rule evaluators, and API endpoints for issue/summary/entity views. Keep current behavior for existing snapshot APIs while adding publish-blocking only for `FAIL`.

**Tech Stack:** FastAPI, SQLAlchemy, Alembic, pytest, Playwright (regression unaffected).

---

### Task 1: Add Quality Persistence Schema

**Files:**
- Create: `backend/app/models/quality.py`
- Modify: `backend/app/models/__init__.py`
- Create: `backend/alembic/versions/20260214_02_quality_tables.py`
- Test: `backend/tests/test_quality_schema_tables.py`

**Step 1: Write the failing test** (@test-driven-development)
```python
def test_quality_tables_exist(db_engine):
    expected = {"data_quality_issue", "data_quality_summary_daily", "snapshot_publish_log"}
    assert expected.issubset(set(inspect(db_engine).get_table_names()))
```

**Step 2: Run test to verify it fails**

Run: `cd backend; python -m pytest tests/test_quality_schema_tables.py -v`  
Expected: FAIL because tables do not exist.

**Step 3: Write minimal implementation**
```python
class DataQualityIssue(Base): ...
class DataQualitySummaryDaily(Base): ...
class SnapshotPublishLog(Base): ...
```

**Step 4: Run test to verify it passes**

Run: `cd backend; python -m alembic upgrade head; python -m pytest tests/test_quality_schema_tables.py -v`  
Expected: PASS.

**Step 5: Commit**
```bash
git add backend/app/models backend/alembic backend/tests/test_quality_schema_tables.py
git commit -m "feat: add data quality persistence schema"
```

### Task 2: Build Common Quality Rule Engine

**Files:**
- Create: `backend/app/quality/rules/common.py`
- Create: `backend/app/quality/types.py`
- Create: `backend/app/quality/engine.py`
- Test: `backend/tests/quality/test_common_rules.py`

**Step 1: Write the failing test**
```python
def test_required_key_rule_fails_when_missing():
    issues = check_required_keys({"corp_name": "alpha"}, ["corp_code"])
    assert issues[0].severity == "FAIL"
```

**Step 2: Run test to verify it fails**

Run: `cd backend; python -m pytest tests/quality/test_common_rules.py -v`  
Expected: FAIL with missing module/function.

**Step 3: Write minimal implementation**
```python
def check_required_keys(payload, keys): ...
def check_date_format(value): ...
def check_numeric(value, allow_negative=False): ...
```

**Step 4: Run test to verify it passes**

Run: `cd backend; python -m pytest tests/quality/test_common_rules.py -v`  
Expected: PASS.

**Step 5: Commit**
```bash
git add backend/app/quality backend/tests/quality/test_common_rules.py
git commit -m "feat: add common data quality rule engine"
```

### Task 3: Add DART/KIND/KRX Rule Packs

**Files:**
- Create: `backend/app/quality/rules/dart.py`
- Create: `backend/app/quality/rules/kind.py`
- Create: `backend/app/quality/rules/krx.py`
- Create: `backend/app/quality/rules/cross_source.py`
- Test: `backend/tests/quality/test_dart_rules.py`
- Test: `backend/tests/quality/test_kind_rules.py`
- Test: `backend/tests/quality/test_krx_rules.py`
- Test: `backend/tests/quality/test_cross_source_rules.py`

**Step 1: Write the failing test**
```python
def test_kind_stage_rule_fails_for_unknown_stage():
    issues = evaluate_kind_rules({"stage": "UNKNOWN"})
    assert any(i.rule_code == "KIND_STAGE_ALLOWED" and i.severity == "FAIL" for i in issues)
```

**Step 2: Run test to verify it fails**

Run: `cd backend; python -m pytest tests/quality/test_dart_rules.py tests/quality/test_kind_rules.py tests/quality/test_krx_rules.py tests/quality/test_cross_source_rules.py -v`  
Expected: FAIL with missing evaluators.

**Step 3: Write minimal implementation**
```python
def evaluate_dart_rules(row): ...
def evaluate_kind_rules(row): ...
def evaluate_krx_rules(row, registry): ...
def evaluate_cross_source(kind_rows, dart_rows, krx_rows): ...
```

**Step 4: Run test to verify it passes**

Run: `cd backend; python -m pytest tests/quality/test_dart_rules.py tests/quality/test_kind_rules.py tests/quality/test_krx_rules.py tests/quality/test_cross_source_rules.py -v`  
Expected: PASS.

**Step 5: Commit**
```bash
git add backend/app/quality/rules backend/tests/quality
git commit -m "feat: add source-specific and cross-source quality rules"
```

### Task 4: Integrate Quality Gate into ETL Publish Path

**Files:**
- Modify: `backend/app/etl/pipeline.py`
- Create: `backend/app/quality/gate.py`
- Create: `backend/app/services/quality_log_service.py`
- Test: `backend/tests/etl/test_quality_gate_publish.py`

**Step 1: Write the failing test**
```python
def test_fail_issue_blocks_snapshot_publish(db_session):
    result = run_pipeline(db_session, fixture_bundle_with_fail)
    assert result.published is False
```

**Step 2: Run test to verify it fails**

Run: `cd backend; python -m pytest tests/etl/test_quality_gate_publish.py -v`  
Expected: FAIL because gate is not integrated.

**Step 3: Write minimal implementation**
```python
gate_result = run_quality_gate(bundle)
if gate_result.has_fail:
    save_publish_log(published=False, blocked_reason="quality_fail")
    return
publish_snapshot(...)
```

**Step 4: Run test to verify it passes**

Run: `cd backend; python -m pytest tests/etl/test_quality_gate_publish.py -v`  
Expected: PASS.

**Step 5: Commit**
```bash
git add backend/app/etl/pipeline.py backend/app/quality/gate.py backend/app/services/quality_log_service.py backend/tests/etl/test_quality_gate_publish.py
git commit -m "feat: integrate quality gate into snapshot publish flow"
```

### Task 5: Expose Quality APIs

**Files:**
- Create: `backend/app/api/endpoints/quality.py`
- Modify: `backend/app/api/router.py`
- Create: `backend/tests/api/test_quality_api.py`

**Step 1: Write the failing test**
```python
def test_quality_summary_api_returns_source_counts(client):
    r = client.get("/api/v1/quality/summary")
    assert r.status_code == 200
    assert "items" in r.json()
```

**Step 2: Run test to verify it fails**

Run: `cd backend; python -m pytest tests/api/test_quality_api.py -v`  
Expected: FAIL with 404.

**Step 3: Write minimal implementation**
```python
@router.get("/quality/issues") ...
@router.get("/quality/summary") ...
@router.get("/quality/entity/{entity_key}") ...
```

**Step 4: Run test to verify it passes**

Run: `cd backend; python -m pytest tests/api/test_quality_api.py -v`  
Expected: PASS.

**Step 5: Commit**
```bash
git add backend/app/api/endpoints/quality.py backend/app/api/router.py backend/tests/api/test_quality_api.py
git commit -m "feat: add quality reporting APIs"
```

### Task 6: Add Daily Summary Job and Aggregation

**Files:**
- Modify: `backend/app/jobs/tasks.py`
- Modify: `backend/app/jobs/schedules.py`
- Create: `backend/app/services/quality_summary_service.py`
- Test: `backend/tests/jobs/test_quality_summary_job.py`

**Step 1: Write the failing test**
```python
def test_quality_summary_job_writes_daily_rows(db_session):
    run_quality_summary_job(db_session, "2026-02-14")
    assert get_summary_count(db_session) > 0
```

**Step 2: Run test to verify it fails**

Run: `cd backend; python -m pytest tests/jobs/test_quality_summary_job.py -v`  
Expected: FAIL because job/service is missing.

**Step 3: Write minimal implementation**
```python
def aggregate_quality_daily(session, date): ...
def run_quality_summary_job(...): ...
```

**Step 4: Run test to verify it passes**

Run: `cd backend; python -m pytest tests/jobs/test_quality_summary_job.py -v`  
Expected: PASS.

**Step 5: Commit**
```bash
git add backend/app/jobs backend/app/services/quality_summary_service.py backend/tests/jobs/test_quality_summary_job.py
git commit -m "feat: add daily data quality summary job"
```

### Task 7: Add End-to-End Quality Regression

**Files:**
- Create: `backend/tests/integration/test_quality_gate_end_to_end.py`
- Modify: `backend/tests/integration/test_end_to_end_ipo_company_flow.py`

**Step 1: Write the failing test**
```python
def test_fail_data_keeps_previous_snapshot(client, seed_bad_batch):
    r = client.get("/api/v1/company/snapshot?corp_code=00126380")
    assert r.status_code == 200
    assert r.json()["partial"] in {True, False}
```

**Step 2: Run test to verify it fails**

Run: `cd backend; python -m pytest tests/integration/test_quality_gate_end_to_end.py -v`  
Expected: FAIL until gate behavior is wired.

**Step 3: Write minimal implementation**
```python
# add fixture helpers and publish fallback behavior assertions
```

**Step 4: Run test to verify it passes**

Run: `cd backend; python -m pytest tests/integration/test_quality_gate_end_to_end.py tests/integration/test_end_to_end_ipo_company_flow.py -v`  
Expected: PASS.

**Step 5: Commit**
```bash
git add backend/tests/integration
git commit -m "test: add quality gate end-to-end regression coverage"
```

### Task 8: Update Documentation and Final Verification

**Files:**
- Modify: `docs/openapi.yaml`
- Modify: `docs/operations/runbook.md`
- Modify: `README.md`

**Step 1: Write the failing test**
```python
def test_quality_endpoints_documented():
    # parse openapi yaml and assert /quality paths exist
```

**Step 2: Run test to verify it fails**

Run: `cd backend; python -m pytest tests/api/test_quality_api_docs.py -v`  
Expected: FAIL before doc updates.

**Step 3: Write minimal implementation**
```yaml
/quality/issues:
/quality/summary:
/quality/entity/{entity_key}:
```

**Step 4: Run test to verify it passes**

Run:
- `cd backend; python -m pytest -q`
- `cd web; npm test`
- `cd web; npx playwright test`

Expected: all PASS.

**Step 5: Commit**
```bash
git add README.md docs/openapi.yaml docs/operations/runbook.md
git commit -m "docs: add data quality operations and API references"
```

### Global Verification Checklist (@verification-before-completion)

- Run: `cd backend; python -m alembic upgrade head`
- Run: `cd backend; python -m pytest -q`
- Run: `cd backend; python -m pytest tests/integration -v`
- Run: `cd web; npm test`
- Run: `cd web; npx playwright test`
- Run: API smoke:
  - `GET /api/v1/quality/issues`
  - `GET /api/v1/quality/summary`
  - `GET /api/v1/quality/entity/00126380`

