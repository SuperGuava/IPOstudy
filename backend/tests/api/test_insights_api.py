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

