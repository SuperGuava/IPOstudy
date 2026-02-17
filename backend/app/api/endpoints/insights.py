from fastapi import APIRouter, HTTPException, Query

from app.db.session import SessionLocal
from app.services.insight_service import get_company_insight_detail, list_analysis_templates, list_companies_for_explorer
from app.services.ipo_service import ensure_demo_pipeline_if_empty

router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("/companies")
def get_insight_companies(
    query: str | None = None,
    limit: int = Query(default=30, ge=1, le=200),
) -> dict:
    with SessionLocal() as session:
        ensure_demo_pipeline_if_empty(session)
        items = list_companies_for_explorer(session, query=query, limit=limit)
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

