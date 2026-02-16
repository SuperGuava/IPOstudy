from fastapi.testclient import TestClient

from app.main import app


def test_ipo_pipeline_api() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/ipo/pipeline")
    assert response.status_code == 200
    body = response.json()
    assert "items" in body
    assert "total" in body
    assert isinstance(body["items"], list)
    assert body["total"] == len(body["items"])


def test_ipo_detail_api() -> None:
    client = TestClient(app)
    pipeline = client.get("/api/v1/ipo/pipeline").json()["items"]
    assert pipeline
    target_id = pipeline[0]["pipeline_id"]

    response = client.get(f"/api/v1/ipo/{target_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["pipeline_id"] == target_id


def test_ipo_detail_returns_404_for_missing_pipeline() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/ipo/__missing_pipeline_id__")
    assert response.status_code == 404
