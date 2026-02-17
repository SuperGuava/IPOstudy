from fastapi import APIRouter, HTTPException, Query

from app.db.session import SessionLocal
from app.services.insight_service import (
    build_beginner_report,
    compare_company_insights,
    get_company_insight_detail,
    get_insight_overview,
    list_analysis_templates,
    list_companies_for_explorer,
)
from app.services.ipo_service import ensure_demo_pipeline_if_empty

router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("/companies")
def get_insight_companies(
    query: str | None = None,
    stage: str | None = None,
    risk_label: str | None = Query(default=None, pattern="^(low|medium|high)$"),
    limit: int = Query(default=30, ge=1, le=200),
) -> dict:
    with SessionLocal() as session:
        ensure_demo_pipeline_if_empty(session)
        items = list_companies_for_explorer(session, query=query, stage=stage, risk_label=risk_label, limit=limit)
    return {"items": items, "total": len(items)}


@router.get("/company")
def get_insight_company(company_key: str) -> dict:
    with SessionLocal() as session:
        ensure_demo_pipeline_if_empty(session)
        detail = get_company_insight_detail(session, company_key=company_key)
    if detail is None:
        raise HTTPException(status_code=404, detail="company insight not found")
    return detail


@router.get("/templates")
def get_insight_templates() -> dict:
    items = list_analysis_templates()
    return {"items": items, "total": len(items)}


@router.get("/overview")
def get_insights_overview() -> dict:
    with SessionLocal() as session:
        ensure_demo_pipeline_if_empty(session)
        return get_insight_overview(session)


@router.get("/compare")
def get_insight_compare(
    company_key: list[str] = Query(default=[]),
) -> dict:
    with SessionLocal() as session:
        ensure_demo_pipeline_if_empty(session)
        return compare_company_insights(session, company_keys=company_key)


@router.get("/report")
def get_insight_report(company_key: str, template_id: str) -> dict:
    with SessionLocal() as session:
        ensure_demo_pipeline_if_empty(session)
        report = build_beginner_report(session, company_key=company_key, template_id=template_id)
    if report is None:
        raise HTTPException(status_code=404, detail="insight report not found")
    return report
