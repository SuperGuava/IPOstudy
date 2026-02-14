def normalize_kind_rows(rows: list[dict]) -> list[dict]:
    normalized: list[dict] = []
    for row in rows:
        normalized.append(
            {
                "corp_name": row.get("corp_name", "").strip(),
                "market": row.get("market"),
                "stage": row.get("stage", "").strip(),
                "listing_date": row.get("listing_date"),
                "lead_manager": row.get("lead_manager"),
            }
        )
    return normalized


def normalize_dart_disclosures(rows: list[dict]) -> list[dict]:
    normalized: list[dict] = []
    for row in rows:
        normalized.append(
            {
                "corp_code": row.get("corp_code"),
                "corp_name": row.get("corp_name", "").strip(),
                "rcept_no": row.get("rcept_no"),
                "report_nm": row.get("report_nm"),
                "rcept_dt": row.get("rcept_dt"),
            }
        )
    return normalized
