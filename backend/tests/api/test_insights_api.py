from fastapi.testclient import TestClient

from app.main import app


def test_insight_companies_returns_items() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/insights/companies")
    assert response.status_code == 200
    body = response.json()
    assert "items" in body
    assert "total" in body
    assert body["total"] >= 1
    first = body["items"][0]
    assert "company_key" in first
    assert "corp_name" in first
    assert "risk_label" in first


def test_insight_company_detail_works_with_listed_key() -> None:
    client = TestClient(app)
    companies = client.get("/api/v1/insights/companies").json()["items"]
    company_key = companies[0]["company_key"]
    response = client.get("/api/v1/insights/company", params={"company_key": company_key})
    assert response.status_code == 200
    body = response.json()
    assert body["company_key"] == company_key
    assert "beginner_summary" in body
    assert isinstance(body["quick_insights"], list)


def test_insight_templates_returns_default_templates() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/insights/templates")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 3
    ids = {row["template_id"] for row in body["items"]}
    assert "foundation-check" in ids


def test_insight_overview_returns_aggregates() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/insights/overview")
    assert response.status_code == 200
    body = response.json()
    assert "total_companies" in body
    assert "stage_counts" in body
    assert "risk_counts" in body
    assert "top_lead_managers" in body


def test_insight_companies_supports_stage_and_risk_filters() -> None:
    client = TestClient(app)
    baseline = client.get("/api/v1/insights/companies", params={"limit": 5})
    assert baseline.status_code == 200
    first = baseline.json()["items"][0]
    response = client.get(
        "/api/v1/insights/companies",
        params={"stage": first["stage"], "risk_label": first["risk_label"], "limit": 20},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 1
    for row in body["items"]:
        assert row["stage"] == first["stage"]
        assert row["risk_label"] == first["risk_label"]


def test_insight_compare_returns_summary_for_multiple_companies() -> None:
    client = TestClient(app)
    companies = client.get("/api/v1/insights/companies", params={"limit": 3}).json()["items"]
    keys = [row["company_key"] for row in companies]
    response = client.get("/api/v1/insights/compare", params=[("company_key", key) for key in keys])
    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 2
    assert "summary" in body
    assert "max_fail" in body["summary"]


def test_insight_report_returns_beginner_report() -> None:
    client = TestClient(app)
    company_key = client.get("/api/v1/insights/companies", params={"limit": 1}).json()["items"][0]["company_key"]
    response = client.get(
        "/api/v1/insights/report",
        params={"company_key": company_key, "template_id": "foundation-check"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["company_key"] == company_key
    assert body["template_id"] == "foundation-check"
    assert isinstance(body["report_lines"], list)
    assert len(body["report_lines"]) >= 3
