from fastapi.testclient import TestClient

from app.main import app


def test_end_to_end_ipo_company_flow() -> None:
    client = TestClient(app)

    pipeline_response = client.get("/api/v1/ipo/pipeline")
    assert pipeline_response.status_code == 200

    items = pipeline_response.json()["items"]
    assert items
    # Live KIND snapshot rows can omit corp_code when DART linkage is unavailable.
    corp_code = next((item.get("corp_code") for item in items if item.get("corp_code")), "00126380")
    assert corp_code

    snapshot_response = client.get("/api/v1/company/snapshot", params={"corp_code": corp_code})
    assert snapshot_response.status_code == 200
    snapshot_body = snapshot_response.json()
    assert "profile" in snapshot_body
    assert snapshot_body["corp_code"] == corp_code
    assert "source_status" in snapshot_body
