from fastapi.testclient import TestClient

from app.main import app


def test_quality_summary_api_returns_source_counts() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/quality/summary")
    assert response.status_code == 200
    body = response.json()
    assert "items" in body
    assert isinstance(body["items"], list)


def test_quality_issues_api_returns_list() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/quality/issues", params={"source": "DART"})
    assert response.status_code == 200
    body = response.json()
    assert "items" in body


def test_quality_entity_api_returns_history() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/quality/entity/00126380")
    assert response.status_code == 200
    body = response.json()
    assert body["entity_key"] == "00126380"
    assert "items" in body


def test_quality_overview_api_returns_aggregates() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/quality/overview")
    assert response.status_code == 200
    body = response.json()
    assert "total_issues" in body
    assert "severity_counts" in body
    assert "source_counts" in body


def test_quality_rules_api_returns_catalog() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/quality/rules")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] > 0
    rule_codes = {row["rule_code"] for row in body["items"]}
    assert "KRX_RESPONSE_SCHEMA" in rule_codes


def test_quality_rules_api_filters_by_source_and_severity() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/quality/rules", params={"source": "KRX", "severity": "FAIL"})
    assert response.status_code == 200
    body = response.json()
    assert body["total"] > 0
    for row in body["items"]:
        assert row["source"] == "KRX"
        assert row["severity"] == "FAIL"
