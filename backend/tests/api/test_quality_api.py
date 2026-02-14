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
