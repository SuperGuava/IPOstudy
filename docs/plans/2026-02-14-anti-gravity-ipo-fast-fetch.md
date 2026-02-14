# Anti-Gravity IPO Fast Fetch Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a production-ready MVP that ingests DART/KIND/KRX data, normalizes and snapshots it, serves fast APIs, and provides a full Next.js dashboard with Excel export.

**Architecture:** Use a modular monolith. Backend (FastAPI) owns connectors, ETL, jobs, and APIs. PostgreSQL stores normalized/snapshot data, Redis+Celery handles async jobs. Frontend (Next.js) consumes backend APIs.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy, Alembic, Celery, Redis, PostgreSQL, Node.js 22, Next.js 15, TypeScript, Playwright, pytest.

---

### Task 1: Scaffold Repository and Runtime

**Files:**
- Create: `backend/pyproject.toml`
- Create: `backend/app/main.py`
- Create: `backend/app/core/config.py`
- Create: `backend/app/core/logging.py`
- Create: `backend/app/api/router.py`
- Create: `backend/tests/test_health.py`
- Create: `infra/docker-compose.yml`
- Create: `.env.example`
- Create: `web/package.json`
- Create: `web/next.config.ts`
- Create: `web/tsconfig.json`
- Create: `web/app/page.tsx`

**Step 1: Write the failing test** (@test-driven-development)
```python
# backend/tests/test_health.py
from fastapi.testclient import TestClient
from app.main import app

def test_health():
    client = TestClient(app)
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
```

**Step 2: Run test to verify it fails**

Run: `cd backend; pytest tests/test_health.py -v`  
Expected: FAIL with import/app setup errors.

**Step 3: Write minimal implementation**
```python
# backend/app/main.py
from fastapi import FastAPI
from app.api.router import api_router

app = FastAPI(title="Anti-Gravity API")
app.include_router(api_router, prefix="/api/v1")

# backend/app/api/router.py
from fastapi import APIRouter

api_router = APIRouter()

@api_router.get("/health")
def health():
    return {"status": "ok"}
```

**Step 4: Run test to verify it passes**

Run: `cd backend; pytest tests/test_health.py -v`  
Expected: PASS.

**Step 5: Commit**
```bash
git add backend infra .env.example web
git commit -m "chore: scaffold backend frontend and infra runtime"
```

### Task 2: Define Database Schema and Migrations

**Files:**
- Create: `backend/app/db/base.py`
- Create: `backend/app/db/session.py`
- Create: `backend/app/models/corp.py`
- Create: `backend/app/models/disclosure.py`
- Create: `backend/app/models/ipo.py`
- Create: `backend/app/models/snapshot.py`
- Create: `backend/alembic.ini`
- Create: `backend/alembic/env.py`
- Create: `backend/alembic/versions/20260214_01_init_schema.py`
- Create: `backend/tests/test_schema_tables.py`

**Step 1: Write the failing test**
```python
def test_core_tables_exist(db_engine):
    expected = {
        "corp_master",
        "corp_profile",
        "dart_disclosure",
        "ipo_pipeline_item",
        "company_snapshot",
        "ipo_pipeline_snapshot",
        "dataset_registry",
        "raw_payload_log",
    }
    assert expected.issubset(set(inspect(db_engine).get_table_names()))
```

**Step 2: Run test to verify it fails**

Run: `cd backend; pytest tests/test_schema_tables.py -v`  
Expected: FAIL because tables do not exist.

**Step 3: Write minimal implementation**
```python
# create SQLAlchemy models + initial Alembic migration for required tables
```

**Step 4: Run test to verify it passes**

Run: `cd backend; alembic upgrade head && pytest tests/test_schema_tables.py -v`  
Expected: PASS.

**Step 5: Commit**
```bash
git add backend/app/db backend/app/models backend/alembic* backend/tests
git commit -m "feat: add initial normalized and snapshot schema"
```

### Task 3: Implement DART Connector and Parsing

**Files:**
- Create: `backend/app/connectors/dart_connector.py`
- Create: `backend/app/connectors/http_client.py`
- Create: `backend/app/schemas/dart.py`
- Create: `backend/tests/connectors/test_dart_connector.py`
- Create: `backend/tests/fixtures/dart/list_response.json`
- Create: `backend/tests/fixtures/dart/company_response.json`
- Create: `backend/tests/fixtures/dart/estkRs_response.json`

**Step 1: Write the failing test**
```python
def test_fetch_list_parses_items(mock_dart):
    items = mock_dart.fetch_list("00126380")
    assert items
    assert "rcept_no" in items[0]
```

**Step 2: Run test to verify it fails**

Run: `cd backend; pytest tests/connectors/test_dart_connector.py -v`  
Expected: FAIL with missing connector.

**Step 3: Write minimal implementation**
```python
# implement methods:
# - fetch_corp_codes_zip()
# - fetch_company(corp_code)
# - fetch_list(...)
# - fetch_document_zip(rcept_no)
# - fetch_estk_rs(rcept_no)
```

**Step 4: Run test to verify it passes**

Run: `cd backend; pytest tests/connectors/test_dart_connector.py -v`  
Expected: PASS.

**Step 5: Commit**
```bash
git add backend/app/connectors backend/app/schemas backend/tests/connectors backend/tests/fixtures/dart
git commit -m "feat: implement DART connector with typed parsing"
```

### Task 4: Implement KIND and KRX Connectors with Dataset Registry

**Files:**
- Create: `backend/app/connectors/kind_connector.py`
- Create: `backend/app/connectors/krx_connector.py`
- Create: `backend/app/services/dataset_registry_service.py`
- Create: `backend/tests/connectors/test_kind_connector.py`
- Create: `backend/tests/connectors/test_krx_connector.py`
- Create: `backend/tests/services/test_dataset_registry.py`
- Create: `backend/tests/fixtures/kind/*.html`
- Create: `backend/tests/fixtures/krx/*.json`

**Step 1: Write the failing test**
```python
def test_krx_connector_uses_registry_bld(mock_db, mock_http):
    row = {"dataset_key": "stock.marketcap", "bld": "dbms/MDC/STAT/standard/MDCSTAT01501"}
    mock_db.seed_dataset(row)
    data = fetch_dataset("stock.marketcap", {"trdDd": "20260213"})
    assert "OutBlock_1" in data
```

**Step 2: Run test to verify it fails**

Run: `cd backend; pytest tests/connectors/test_kind_connector.py tests/connectors/test_krx_connector.py tests/services/test_dataset_registry.py -v`  
Expected: FAIL.

**Step 3: Write minimal implementation**
```python
# implement KIND parsers and KRX POST endpoint caller
# enforce registry lookup before request
```

**Step 4: Run test to verify it passes**

Run: `cd backend; pytest tests/connectors/test_kind_connector.py tests/connectors/test_krx_connector.py tests/services/test_dataset_registry.py -v`  
Expected: PASS.

**Step 5: Commit**
```bash
git add backend/app/connectors backend/app/services backend/tests/connectors backend/tests/services backend/tests/fixtures
git commit -m "feat: add KIND and KRX connectors with dataset registry"
```

### Task 5: Build ETL Normalize and Reconcile Pipeline

**Files:**
- Create: `backend/app/etl/raw_ingest.py`
- Create: `backend/app/etl/normalize.py`
- Create: `backend/app/etl/reconcile.py`
- Create: `backend/app/etl/pipeline.py`
- Create: `backend/tests/etl/test_normalize.py`
- Create: `backend/tests/etl/test_reconcile.py`
- Create: `backend/tests/etl/test_pipeline_e2e.py`

**Step 1: Write the failing test**
```python
def test_pipeline_builds_ipo_item_from_kind_and_dart(db_session, fixture_bundle):
    run_pipeline(fixture_bundle)
    item = db_session.execute(select(IPOPipelineItem)).scalar_one()
    assert item.corp_code is not None
    assert item.stage in {"예비심사", "공모", "상장예정", "신규상장"}
```

**Step 2: Run test to verify it fails**

Run: `cd backend; pytest tests/etl/test_pipeline_e2e.py -v`  
Expected: FAIL.

**Step 3: Write minimal implementation**
```python
# raw save -> normalize rows -> apply matching rules -> persist ipo_pipeline_item
```

**Step 4: Run test to verify it passes**

Run: `cd backend; pytest tests/etl/test_normalize.py tests/etl/test_reconcile.py tests/etl/test_pipeline_e2e.py -v`  
Expected: PASS.

**Step 5: Commit**
```bash
git add backend/app/etl backend/tests/etl
git commit -m "feat: implement normalize and reconcile ETL pipeline"
```

### Task 6: Build Snapshot Builder and Partial Response Contract

**Files:**
- Create: `backend/app/services/snapshot_service.py`
- Create: `backend/app/services/source_status_service.py`
- Create: `backend/app/schemas/snapshot.py`
- Create: `backend/tests/services/test_snapshot_service.py`
- Create: `backend/tests/services/test_partial_response.py`

**Step 1: Write the failing test**
```python
def test_company_snapshot_partial_when_krx_fails(db_session, seed_company):
    response = build_company_snapshot(seed_company.corp_code, krx_failed=True)
    assert response.partial is True
    assert "krx_market" in response.missing_sections
```

**Step 2: Run test to verify it fails**

Run: `cd backend; pytest tests/services/test_snapshot_service.py tests/services/test_partial_response.py -v`  
Expected: FAIL.

**Step 3: Write minimal implementation**
```python
# snapshot assembler + source_status fields
```

**Step 4: Run test to verify it passes**

Run: `cd backend; pytest tests/services/test_snapshot_service.py tests/services/test_partial_response.py -v`  
Expected: PASS.

**Step 5: Commit**
```bash
git add backend/app/services backend/app/schemas backend/tests/services
git commit -m "feat: add snapshot builder with partial response policy"
```

### Task 7: Expose Serving API and Excel Export

**Files:**
- Create: `backend/app/api/endpoints/company.py`
- Create: `backend/app/api/endpoints/ipo.py`
- Create: `backend/app/api/endpoints/export.py`
- Modify: `backend/app/api/router.py`
- Create: `backend/app/services/export_service.py`
- Create: `backend/tests/api/test_company_api.py`
- Create: `backend/tests/api/test_ipo_api.py`
- Create: `backend/tests/api/test_export_api.py`

**Step 1: Write the failing test**
```python
def test_export_ipo_xlsx_returns_file(client):
    r = client.get("/api/v1/export/ipo.xlsx")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
```

**Step 2: Run test to verify it fails**

Run: `cd backend; pytest tests/api/test_company_api.py tests/api/test_ipo_api.py tests/api/test_export_api.py -v`  
Expected: FAIL.

**Step 3: Write minimal implementation**
```python
# endpoint wiring + query/service + xlsx generation
```

**Step 4: Run test to verify it passes**

Run: `cd backend; pytest tests/api/test_company_api.py tests/api/test_ipo_api.py tests/api/test_export_api.py -v`  
Expected: PASS.

**Step 5: Commit**
```bash
git add backend/app/api backend/app/services/export_service.py backend/tests/api
git commit -m "feat: expose snapshot APIs and excel export endpoints"
```

### Task 8: Add Celery Jobs and Schedulers

**Files:**
- Create: `backend/app/jobs/celery_app.py`
- Create: `backend/app/jobs/tasks.py`
- Create: `backend/app/jobs/schedules.py`
- Create: `backend/tests/jobs/test_tasks.py`
- Create: `backend/tests/jobs/test_scheduler.py`

**Step 1: Write the failing test**
```python
def test_dart_trigger_enqueues_company_refresh(celery_app, mocker):
    enqueue_refresh_for_disclosure({"corp_code": "00126380"})
    mocker.patch("app.jobs.tasks.refresh_company_snapshot").assert_called_once()
```

**Step 2: Run test to verify it fails**

Run: `cd backend; pytest tests/jobs/test_tasks.py tests/jobs/test_scheduler.py -v`  
Expected: FAIL.

**Step 3: Write minimal implementation**
```python
# periodic and event-driven tasks
```

**Step 4: Run test to verify it passes**

Run: `cd backend; pytest tests/jobs/test_tasks.py tests/jobs/test_scheduler.py -v`  
Expected: PASS.

**Step 5: Commit**
```bash
git add backend/app/jobs backend/tests/jobs
git commit -m "feat: add celery periodic and incremental refresh jobs"
```

### Task 9: Build Next.js Dashboard (IPO Board, Deal Detail, Company Snapshot)

**Files:**
- Create: `web/app/ipo/page.tsx`
- Create: `web/app/ipo/[pipelineId]/page.tsx`
- Create: `web/app/company/[corpCode]/page.tsx`
- Create: `web/components/ipo-board.tsx`
- Create: `web/components/ipo-detail.tsx`
- Create: `web/components/company-card.tsx`
- Create: `web/lib/api.ts`
- Create: `web/tests/e2e/ipo-flow.spec.ts`

**Step 1: Write the failing test**
```ts
// web/tests/e2e/ipo-flow.spec.ts
import { test, expect } from "@playwright/test";

test("navigate ipo board to detail", async ({ page }) => {
  await page.goto("/ipo");
  await page.getByRole("row").nth(1).click();
  await expect(page).toHaveURL(/\/ipo\/.+/);
});
```

**Step 2: Run test to verify it fails**

Run: `cd web; npx playwright test web/tests/e2e/ipo-flow.spec.ts`  
Expected: FAIL.

**Step 3: Write minimal implementation**
```tsx
// pages and components consuming backend APIs
```

**Step 4: Run test to verify it passes**

Run: `cd web; npx playwright test web/tests/e2e/ipo-flow.spec.ts`  
Expected: PASS.

**Step 5: Commit**
```bash
git add web
git commit -m "feat: add full dashboard for ipo pipeline and company snapshot"
```

### Task 10: Final Hardening, Docs, and Verification

**Files:**
- Create: `README.md`
- Create: `docs/openapi.yaml`
- Create: `docs/operations/runbook.md`
- Create: `backend/tests/integration/test_end_to_end_ipo_company_flow.py`

**Step 1: Write the failing test**
```python
def test_end_to_end_ipo_company_flow(client, seeded_data):
    p = client.get("/api/v1/ipo/pipeline")
    assert p.status_code == 200
    corp_code = p.json()["items"][0]["corp_code"]
    c = client.get(f"/api/v1/company/snapshot?corp_code={corp_code}")
    assert c.status_code == 200
    assert "profile" in c.json()
```

**Step 2: Run test to verify it fails**

Run: `cd backend; pytest tests/integration/test_end_to_end_ipo_company_flow.py -v`  
Expected: FAIL initially.

**Step 3: Write minimal implementation**
```text
Fill remaining integration gaps and publish docs.
```

**Step 4: Run test to verify it passes**

Run:
- `cd backend; pytest -q`
- `cd web; npm test`
- `cd web; npx playwright test`

Expected: all PASS.

**Step 5: Commit**
```bash
git add README.md docs backend/tests/integration
git commit -m "chore: finalize docs and end-to-end verification"
```

### Global Verification Checklist (@verification-before-completion)

- Run: `cd backend; pytest -q`
- Run: `cd backend; ruff check .`
- Run: `cd backend; mypy app`
- Run: `cd web; npm run lint`
- Run: `cd web; npm run test`
- Run: `cd web; npx playwright test`
- Run: `docker compose -f infra/docker-compose.yml up -d`
- Run: API smoke test for:
  - `/api/v1/company/snapshot`
  - `/api/v1/ipo/pipeline`
  - `/api/v1/ipo/{pipeline_id}`
  - `/api/v1/export/ipo.xlsx`

