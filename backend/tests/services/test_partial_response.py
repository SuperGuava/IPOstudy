from app.services.snapshot_service import build_company_snapshot


def test_company_snapshot_partial_when_krx_fails() -> None:
    response = build_company_snapshot(
        corp_code="00126380",
        payload={"profile": {"corp_name": "알파테크"}, "disclosures": [], "financials": {}},
        krx_failed=True,
    )
    assert response.partial is True
    assert "krx_market" in response.missing_sections
    assert response.source_status["krx_market"] == "failed"
