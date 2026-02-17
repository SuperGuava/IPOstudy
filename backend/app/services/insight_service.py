from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.ipo import IpoPipelineItem
from app.models.quality import DataQualityIssue


def _build_company_key(corp_code: str | None, corp_name: str) -> str:
    if corp_code:
        return corp_code
    return f"name:{corp_name}"


def _risk_label(*, fail_count: int, warn_count: int) -> str:
    if fail_count > 0:
        return "high"
    if warn_count > 0:
        return "medium"
    return "low"


def list_analysis_templates() -> list[dict]:
    return [
        {
            "template_id": "foundation-check",
            "title": "Foundation Check",
            "description": "Review stage, listing date, lead manager, and critical quality issues first.",
            "steps": [
                "1) Check current IPO stage",
                "2) Check listing date and lead manager",
                "3) Resolve FAIL issues first",
            ],
        },
        {
            "template_id": "quality-risk-scan",
            "title": "Quality Risk Scan",
            "description": "Review severity/source issue distribution to estimate data reliability risk.",
            "steps": [
                "1) Check FAIL and WARN counts",
                "2) Identify concentrated issue sources",
                "3) Re-collect data or adjust mappings",
            ],
        },
        {
            "template_id": "listing-readiness",
            "title": "Listing Readiness",
            "description": "Interpret offering/prelisting/listed states and choose next monitoring action.",
            "steps": [
                "1) Confirm stage category",
                "2) Check listing date timing",
                "3) Plan next monitoring cadence",
            ],
        },
    ]


def get_validation_framework() -> dict:
    return {
        "status": "conditional_approval",
        "approval_conditions": [
            "Legal review passed for valuation-range expression",
            "Landing page conversion >= 2.0%",
            "Peer matching backtest accuracy >= 70%",
        ],
        "kill_criteria": [
            "Legal review requires unresolvable business-model change",
            "Landing conversion < 1.0%",
            "Backtest accuracy < 60%",
            "MAU < 100 after 3 months",
        ],
        "budget": {
            "legal_review_usd": 1500,
            "landing_ads_usd": 100,
            "infra_12m_usd": 156,
            "total_1y_usd": 1756,
            "revenue_1y_usd": 864,
            "pnl_1y_usd": -892,
        },
    }


def get_insight_overview(session: Session) -> dict:
    rows = session.execute(select(IpoPipelineItem)).scalars().all()
    corp_codes = [row.corp_code for row in rows if row.corp_code]
    quality_counts = _load_quality_counts_by_corp_code(session, corp_codes)

    stage_counts: dict[str, int] = {}
    risk_counts = {"low": 0, "medium": 0, "high": 0}
    lead_manager_counts: dict[str, int] = {}

    for row in rows:
        stage_counts[row.stage] = stage_counts.get(row.stage, 0) + 1
        counts = quality_counts.get(row.corp_code or "", {"PASS": 0, "WARN": 0, "FAIL": 0})
        risk = _risk_label(fail_count=counts["FAIL"], warn_count=counts["WARN"])
        risk_counts[risk] += 1
        if row.lead_manager:
            lead_manager_counts[row.lead_manager] = lead_manager_counts.get(row.lead_manager, 0) + 1

    top_lead_managers = [
        {"lead_manager": key, "count": value}
        for key, value in sorted(lead_manager_counts.items(), key=lambda item: item[1], reverse=True)[:5]
    ]

    return {
        "total_companies": len(rows),
        "stage_counts": stage_counts,
        "risk_counts": risk_counts,
        "top_lead_managers": top_lead_managers,
    }


def _build_quick_insights(
    *,
    corp_name: str,
    stage: str,
    listing_date: str | None,
    lead_manager: str | None,
    quality_by_severity: dict[str, int],
) -> list[str]:
    insights = [f"{corp_name} is currently in '{stage}' stage."]
    if listing_date:
        insights.append(f"Reference listing date: {listing_date}.")
    if lead_manager:
        insights.append(f"Lead manager: {lead_manager}.")
    insights.append(
        f"Quality status: FAIL {quality_by_severity['FAIL']}, WARN {quality_by_severity['WARN']}, PASS {quality_by_severity['PASS']}."
    )
    return insights


def _load_quality_counts_by_corp_code(session: Session, corp_codes: list[str]) -> dict[str, dict[str, int]]:
    if not corp_codes:
        return {}
    quality_rows = session.execute(
        select(DataQualityIssue.entity_key, DataQualityIssue.severity, func.count(DataQualityIssue.id))
        .where(DataQualityIssue.entity_key.in_(corp_codes))
        .group_by(DataQualityIssue.entity_key, DataQualityIssue.severity)
    ).all()
    quality_counts: dict[str, dict[str, int]] = {}
    for entity_key, severity, count in quality_rows:
        slot = quality_counts.setdefault(str(entity_key), {"PASS": 0, "WARN": 0, "FAIL": 0})
        slot[str(severity)] = int(count)
    return quality_counts


def list_companies_for_explorer(
    session: Session,
    *,
    query: str | None,
    limit: int,
    stage: str | None = None,
    risk_label: str | None = None,
) -> list[dict]:
    stmt = select(IpoPipelineItem).order_by(IpoPipelineItem.listing_date.desc().nullslast(), IpoPipelineItem.corp_name.asc())
    if query:
        q = query.strip()
        if q:
            pattern = f"%{q}%"
            stmt = stmt.where(or_(IpoPipelineItem.corp_name.ilike(pattern), IpoPipelineItem.corp_code.ilike(pattern)))
    if stage:
        stmt = stmt.where(IpoPipelineItem.stage == stage)

    fetch_limit = min(1000, max(limit, limit * 5 if risk_label else limit))
    rows = session.execute(stmt.limit(fetch_limit)).scalars().all()
    corp_codes = [row.corp_code for row in rows if row.corp_code]
    quality_counts = _load_quality_counts_by_corp_code(session, corp_codes)

    items: list[dict] = []
    for row in rows:
        counts = quality_counts.get(row.corp_code or "", {"PASS": 0, "WARN": 0, "FAIL": 0})
        row_risk_label = _risk_label(fail_count=counts["FAIL"], warn_count=counts["WARN"])
        if risk_label and row_risk_label != risk_label:
            continue
        items.append(
            {
                "company_key": _build_company_key(row.corp_code, row.corp_name),
                "corp_code": row.corp_code,
                "corp_name": row.corp_name,
                "stage": row.stage,
                "listing_date": row.listing_date.isoformat() if row.listing_date else None,
                "lead_manager": row.lead_manager,
                "quality": counts,
                "risk_label": row_risk_label,
            }
        )
        if len(items) >= limit:
            break
    return items


def _resolve_pipeline_row(session: Session, *, company_key: str) -> IpoPipelineItem | None:
    if company_key.startswith("name:"):
        corp_name = company_key.split(":", 1)[1]
        return (
            session.execute(
                select(IpoPipelineItem)
                .where(IpoPipelineItem.corp_name == corp_name)
                .order_by(IpoPipelineItem.listing_date.desc().nullslast())
                .limit(1)
            )
            .scalars()
            .first()
        )
    return (
        session.execute(
            select(IpoPipelineItem)
            .where(IpoPipelineItem.corp_code == company_key)
            .order_by(IpoPipelineItem.listing_date.desc().nullslast())
            .limit(1)
        )
        .scalars()
        .first()
    )


def get_company_insight_detail(session: Session, *, company_key: str) -> dict | None:
    row = _resolve_pipeline_row(session, company_key=company_key)
    if row is None:
        return None

    quality_by_severity = {"PASS": 0, "WARN": 0, "FAIL": 0}
    quality_by_source: dict[str, int] = {}
    if row.corp_code:
        quality_rows = session.execute(
            select(DataQualityIssue.source, DataQualityIssue.severity, func.count(DataQualityIssue.id))
            .where(DataQualityIssue.entity_key == row.corp_code)
            .group_by(DataQualityIssue.source, DataQualityIssue.severity)
        ).all()
        for source, severity, count in quality_rows:
            quality_by_source[str(source)] = quality_by_source.get(str(source), 0) + int(count)
            quality_by_severity[str(severity)] = quality_by_severity.get(str(severity), 0) + int(count)

    listing_date = row.listing_date.isoformat() if row.listing_date else None
    risk_label = _risk_label(fail_count=quality_by_severity["FAIL"], warn_count=quality_by_severity["WARN"])
    quick_insights = _build_quick_insights(
        corp_name=row.corp_name,
        stage=row.stage,
        listing_date=listing_date,
        lead_manager=row.lead_manager,
        quality_by_severity=quality_by_severity,
    )

    beginner_summary = (
        f"{row.corp_name} is in '{row.stage}' stage. "
        f"Start from FAIL {quality_by_severity['FAIL']} issues and then review WARN {quality_by_severity['WARN']}."
    )

    return {
        "company_key": _build_company_key(row.corp_code, row.corp_name),
        "corp_code": row.corp_code,
        "corp_name": row.corp_name,
        "risk_label": risk_label,
        "ipo": {
            "pipeline_id": row.pipeline_id,
            "stage": row.stage,
            "listing_date": listing_date,
            "lead_manager": row.lead_manager,
        },
        "quality": {"severity": quality_by_severity, "source": quality_by_source},
        "beginner_summary": beginner_summary,
        "quick_insights": quick_insights,
    }


def compare_company_insights(session: Session, *, company_keys: list[str]) -> dict:
    unique_keys = list(dict.fromkeys(company_keys))[:5]
    items: list[dict] = []
    for key in unique_keys:
        detail = get_company_insight_detail(session, company_key=key)
        if detail is not None:
            items.append(detail)

    if not items:
        return {
            "items": [],
            "total": 0,
            "summary": {"max_fail": 0, "avg_warn": 0.0, "risk_distribution": {"low": 0, "medium": 0, "high": 0}},
        }

    max_fail = max(item["quality"]["severity"]["FAIL"] for item in items)
    avg_warn = sum(item["quality"]["severity"]["WARN"] for item in items) / len(items)
    risk_distribution = {"low": 0, "medium": 0, "high": 0}
    for item in items:
        risk_distribution[item["risk_label"]] += 1

    return {
        "items": items,
        "total": len(items),
        "summary": {
            "max_fail": max_fail,
            "avg_warn": round(avg_warn, 2),
            "risk_distribution": risk_distribution,
        },
    }


def build_beginner_report(session: Session, *, company_key: str, template_id: str) -> dict | None:
    detail = get_company_insight_detail(session, company_key=company_key)
    if detail is None:
        return None
    templates = {row["template_id"]: row for row in list_analysis_templates()}
    template = templates.get(template_id)
    if template is None:
        return None

    fail_count = detail["quality"]["severity"]["FAIL"]
    warn_count = detail["quality"]["severity"]["WARN"]
    stage = detail["ipo"]["stage"]
    listing_date = detail["ipo"]["listing_date"] or "-"
    lead_manager = detail["ipo"]["lead_manager"] or "-"

    if template_id == "quality-risk-scan":
        report_lines = [
            f"Risk label: {detail['risk_label']}.",
            f"Severity counts -> FAIL {fail_count}, WARN {warn_count}.",
            f"Primary action: focus on sources with repeated FAIL events first.",
            "Secondary action: re-collect data and validate parser mappings.",
        ]
    elif template_id == "listing-readiness":
        report_lines = [
            f"Stage check: current stage is '{stage}'.",
            f"Date check: listing date is {listing_date}.",
            f"Execution check: lead manager is {lead_manager}.",
            f"Quality gate check: FAIL {fail_count}, WARN {warn_count}.",
        ]
    else:
        report_lines = [
            f"Company: {detail['corp_name']}.",
            f"Current stage: {stage}, listing date: {listing_date}, lead manager: {lead_manager}.",
            f"Quality summary: FAIL {fail_count}, WARN {warn_count}.",
            "Recommendation: resolve FAIL first, then handle high-frequency WARN rules.",
        ]

    return {
        "company_key": detail["company_key"],
        "template_id": template_id,
        "template_title": template["title"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "report_lines": report_lines,
    }
