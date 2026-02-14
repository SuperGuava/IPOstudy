def build_source_status(*, dart_failed: bool = False, kind_failed: bool = False, krx_failed: bool = False) -> dict[str, str]:
    return {
        "dart": "failed" if dart_failed else "ok",
        "kind": "failed" if kind_failed else "ok",
        "krx_market": "failed" if krx_failed else "ok",
    }
