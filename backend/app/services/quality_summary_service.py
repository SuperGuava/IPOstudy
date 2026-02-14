from datetime import date, datetime, time

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.quality import DataQualityIssue, DataQualitySummaryDaily


def aggregate_quality_daily(session: Session, summary_date: str) -> int:
    target_day = date.fromisoformat(summary_date)
    day_start = datetime.combine(target_day, time.min)
    day_end = datetime.combine(target_day, time.max)

    rows = (
        session.execute(
            select(DataQualityIssue).where(
                DataQualityIssue.observed_at >= day_start,
                DataQualityIssue.observed_at <= day_end,
            )
        )
        .scalars()
        .all()
    )

    grouped: dict[str, dict[str, int]] = {}
    for row in rows:
        stats = grouped.setdefault(row.source, {"PASS": 0, "WARN": 0, "FAIL": 0})
        stats[row.severity] = stats.get(row.severity, 0) + 1

    if not grouped:
        return 0

    for source in grouped:
        session.execute(
            delete(DataQualitySummaryDaily).where(
                DataQualitySummaryDaily.summary_date == target_day,
                DataQualitySummaryDaily.source == source,
            )
        )

    for source, stats in grouped.items():
        total = stats.get("PASS", 0) + stats.get("WARN", 0) + stats.get("FAIL", 0)
        fail_rate = (stats.get("FAIL", 0) / total) if total > 0 else 0.0
        session.add(
            DataQualitySummaryDaily(
                summary_date=target_day,
                source=source,
                pass_count=stats.get("PASS", 0),
                warn_count=stats.get("WARN", 0),
                fail_count=stats.get("FAIL", 0),
                fail_rate=fail_rate,
            )
        )
    session.commit()
    return len(grouped)
