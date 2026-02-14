from fastapi.testclient import TestClient

from app.main import app


def test_ipo_pipeline_api() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/ipo/pipeline")
    assert response.status_code == 200
    body = response.json()
    assert "items" in body
    assert isinstance(body["items"], list)


def test_ipo_detail_api() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/ipo/alpha-ipo-1")
    assert response.status_code == 200
    body = response.json()
    assert body["pipeline_id"] == "alpha-ipo-1"
