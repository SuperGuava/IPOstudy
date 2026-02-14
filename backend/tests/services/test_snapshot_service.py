from app.services.snapshot_service import build_company_snapshot


def test_company_snapshot_contains_profile() -> None:
    response = build_company_snapshot(
        corp_code="00126380",
        payload={"profile": {"corp_name": "알파테크"}, "disclosures": [], "financials": {}},
        krx_failed=False,
    )
    assert response.corp_code == "00126380"
    assert response.partial is False
    assert response.profile["corp_name"] == "알파테크"
