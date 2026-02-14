from fastapi.testclient import TestClient

from app.main import app


def test_export_ipo_xlsx_returns_file() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/export/ipo.xlsx")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    assert response.content


def test_export_company_xlsx_returns_file() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/export/company/00126380.xlsx")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    assert response.content
