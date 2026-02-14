from collections.abc import Callable


def refresh_company_snapshot(corp_code: str) -> None:
    _ = corp_code


def enqueue_refresh_for_disclosure(
    disclosure: dict,
    refresh_fn: Callable[[str], None] = refresh_company_snapshot,
) -> None:
    corp_code = disclosure.get("corp_code")
    if corp_code:
        refresh_fn(corp_code)
