from app.etl.reconcile import match_kind_with_dart


def test_match_kind_with_dart_by_name() -> None:
    kind_items = [
        {
            "corp_name": "알파테크",
            "stage": "공모",
            "listing_date": "2026-03-15",
            "lead_manager": "미래증권",
        }
    ]
    dart_items = [
        {
            "corp_code": "00126380",
            "corp_name": "알파테크",
            "rcept_no": "20260214000001",
        }
    ]
    matched = match_kind_with_dart(kind_items, dart_items)
    assert matched[0]["corp_code"] == "00126380"
    assert matched[0]["source_dart_rcept_no"] == "20260214000001"
