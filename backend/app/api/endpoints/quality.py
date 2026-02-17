from datetime import date, datetime

from fastapi import APIRouter, Query
from sqlalchemy import Select, and_, select

from app.db.session import SessionLocal
from app.models.quality import DataQualityIssue, DataQualitySummaryDaily
from app.quality.catalog import RULE_CATALOG

router = APIRouter(prefix="/quality", tags=["quality"])


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


@router.get("/issues")
def get_quality_issues(
    source: str | None = None,
    severity: str | None = None,
    rule_code: str | None = None,
    from_date: str | None = Query(default=None, alias="from"),
    to_date: str | None = Query(default=None, alias="to"),
) -> dict:
    stmt: Select = select(DataQualityIssue)
    filters = []
    if source:
        filters.append(DataQualityIssue.source == source)
    if severity:
        filters.append(DataQualityIssue.severity == severity)
    if rule_code:
        filters.append(DataQualityIssue.rule_code == rule_code)
    from_dt = _parse_date(from_date)
    to_dt = _parse_date(to_date)
    if from_dt:
        filters.append(DataQualityIssue.observed_at >= datetime.combine(from_dt, datetime.min.time()))
    if to_dt:
        filters.append(DataQualityIssue.observed_at <= datetime.combine(to_dt, datetime.max.time()))
    if filters:
        stmt = stmt.where(and_(*filters))

    with SessionLocal() as session:
        rows = session.execute(stmt.order_by(DataQualityIssue.id.desc())).scalars().all()
    items = [
        {
            "id": row.id,
            "source": row.source,
            "rule_code": row.rule_code,
            "severity": row.severity,
            "entity_type": row.entity_type,
            "entity_key": row.entity_key,
            "message": row.message,
            "batch_id": row.batch_id,
            "observed_at": row.observed_at.isoformat() if row.observed_at else None,
        }
        for row in rows
    ]
    return {"items": items, "total": len(items)}


@router.get("/summary")
def get_quality_summary(
    source: str | None = None,
    from_date: str | None = Query(default=None, alias="from"),
    to_date: str | None = Query(default=None, alias="to"),
) -> dict:
    stmt: Select = select(DataQualitySummaryDaily)
    filters = []
    if source:
        filters.append(DataQualitySummaryDaily.source == source)
    from_day = _parse_date(from_date)
    to_day = _parse_date(to_date)
    if from_day:
        filters.append(DataQualitySummaryDaily.summary_date >= from_day)
    if to_day:
        filters.append(DataQualitySummaryDaily.summary_date <= to_day)
    if filters:
        stmt = stmt.where(and_(*filters))

    with SessionLocal() as session:
        rows = session.execute(stmt.order_by(DataQualitySummaryDaily.summary_date.desc())).scalars().all()
    items = [
        {
            "summary_date": row.summary_date.isoformat(),
            "source": row.source,
            "pass_count": row.pass_count,
            "warn_count": row.warn_count,
            "fail_count": row.fail_count,
            "fail_rate": row.fail_rate,
        }
        for row in rows
    ]
    return {"items": items, "total": len(items)}


@router.get("/entity/{entity_key}")
def get_quality_entity_history(entity_key: str) -> dict:
    with SessionLocal() as session:
        rows = (
            session.execute(
                select(DataQualityIssue)
                .where(DataQualityIssue.entity_key == entity_key)
                .order_by(DataQualityIssue.id.desc())
            )
            .scalars()
            .all()
        )
    items = [
        {
            "id": row.id,
            "source": row.source,
            "rule_code": row.rule_code,
            "severity": row.severity,
            "message": row.message,
            "observed_at": row.observed_at.isoformat() if row.observed_at else None,
        }
        for row in rows
    ]
    return {"entity_key": entity_key, "items": items, "total": len(items)}


@router.get("/rules")
def get_quality_rule_catalog(
    source: str | None = None,
    severity: str | None = None,
) -> dict:
    rows = RULE_CATALOG
    if source:
        rows = [row for row in rows if row["source"] == source]
    if severity:
        rows = [row for row in rows if row["severity"] == severity]
    return {"items": rows, "total": len(rows)}


@router.get("/overview")
def get_quality_overview(
    source: str | None = None,
    from_date: str | None = Query(default=None, alias="from"),
    to_date: str | None = Query(default=None, alias="to"),
) -> dict:
    stmt: Select = select(DataQualityIssue)
    filters = []
    if source:
        filters.append(DataQualityIssue.source == source)
    from_dt = _parse_date(from_date)
    to_dt = _parse_date(to_date)
    if from_dt:
        filters.append(DataQualityIssue.observed_at >= datetime.combine(from_dt, datetime.min.time()))
    if to_dt:
        filters.append(DataQualityIssue.observed_at <= datetime.combine(to_dt, datetime.max.time()))
    if filters:
        stmt = stmt.where(and_(*filters))

    with SessionLocal() as session:
        rows = session.execute(stmt).scalars().all()

    severity_counts = {"PASS": 0, "WARN": 0, "FAIL": 0}
    source_counts: dict[str, int] = {}
    rule_counts: dict[str, int] = {}
    for row in rows:
        severity_counts[row.severity] = severity_counts.get(row.severity, 0) + 1
        source_counts[row.source] = source_counts.get(row.source, 0) + 1
        rule_counts[row.rule_code] = rule_counts.get(row.rule_code, 0) + 1

    top_rules = sorted(
        ({"rule_code": code, "count": count} for code, count in rule_counts.items()),
        key=lambda item: item["count"],
        reverse=True,
    )[:10]

    return {
        "total_issues": len(rows),
        "severity_counts": severity_counts,
        "source_counts": source_counts,
        "top_rules": top_rules,
    }
