from fastapi.testclient import TestClient

from app.main import app


def test_company_snapshot_api() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/company/snapshot", params={"corp_code": "00126380"})
    assert response.status_code == 200
    body = response.json()
    assert body["corp_code"] == "00126380"
    assert "profile" in body


def test_company_financials_api() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/company/00126380/financials")
    assert response.status_code == 200
    body = response.json()
    assert body["corp_code"] == "00126380"
    assert "financials" in body
