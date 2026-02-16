from datetime import datetime

from fastapi import APIRouter, HTTPException

from app.db.session import SessionLocal
from app.services.ipo_service import (
    ensure_demo_pipeline_if_empty,
    get_pipeline_item,
    list_pipeline_items,
    refresh_pipeline_live,
)

router = APIRouter(prefix="/ipo", tags=["ipo"])


@router.get("/pipeline")
def get_ipo_pipeline(
    refresh: bool = False,
    corp_code: str = "00126380",
    bas_dd: str | None = None,
) -> dict:
    refresh_result: dict | None = None
    run_date = bas_dd or datetime.now().strftime("%Y%m%d")
    with SessionLocal() as session:
        if refresh:
            refresh_result = refresh_pipeline_live(session, corp_code=corp_code, bas_dd=run_date)
        ensure_demo_pipeline_if_empty(session)
        items = list_pipeline_items(session)
    payload: dict = {"items": items, "total": len(items)}
    if refresh_result is not None:
        payload["refresh"] = refresh_result
    return payload


@router.get("/{pipeline_id}")
def get_ipo_detail(pipeline_id: str) -> dict:
    with SessionLocal() as session:
        ensure_demo_pipeline_if_empty(session)
        item = get_pipeline_item(session, pipeline_id)
    if item is None:
        raise HTTPException(status_code=404, detail="pipeline item not found")
    return item
