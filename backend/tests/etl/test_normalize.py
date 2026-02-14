from app.etl.normalize import normalize_dart_disclosures, normalize_kind_rows


def test_normalize_kind_rows() -> None:
    raw_rows = [
        {
            "corp_name": "알파테크",
            "market": "KOSDAQ",
            "stage": "공모",
            "listing_date": "2026-03-15",
            "lead_manager": "미래증권",
        }
    ]
    normalized = normalize_kind_rows(raw_rows)
    assert normalized[0]["corp_name"] == "알파테크"
    assert normalized[0]["stage"] == "공모"


def test_normalize_dart_disclosures() -> None:
    raw_rows = [
        {
            "corp_code": "00126380",
            "corp_name": "알파테크",
            "rcept_no": "20260214000001",
            "report_nm": "증권신고서(지분증권)",
            "rcept_dt": "20260214",
        }
    ]
    normalized = normalize_dart_disclosures(raw_rows)
    assert normalized[0]["corp_code"] == "00126380"
    assert normalized[0]["rcept_no"] == "20260214000001"
