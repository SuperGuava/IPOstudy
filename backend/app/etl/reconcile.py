def match_kind_with_dart(kind_items: list[dict], dart_items: list[dict]) -> list[dict]:
    by_name = {item.get("corp_name"): item for item in dart_items}
    merged: list[dict] = []
    for item in kind_items:
        dart = by_name.get(item.get("corp_name"))
        merged.append(
            {
                **item,
                "corp_code": dart.get("corp_code") if dart else None,
                "source_dart_rcept_no": dart.get("rcept_no") if dart else None,
            }
        )
    return merged
