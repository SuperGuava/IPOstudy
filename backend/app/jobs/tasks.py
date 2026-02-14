from collections.abc import Callable

from sqlalchemy.orm import Session

from app.services.quality_summary_service import aggregate_quality_daily


def refresh_company_snapshot(corp_code: str) -> None:
    _ = corp_code


def enqueue_refresh_for_disclosure(
    disclosure: dict,
    refresh_fn: Callable[[str], None] = refresh_company_snapshot,
) -> None:
    corp_code = disclosure.get("corp_code")
    if corp_code:
        refresh_fn(corp_code)


def run_quality_summary_job(session: Session, summary_date: str) -> int:
    return aggregate_quality_daily(session, summary_date)
