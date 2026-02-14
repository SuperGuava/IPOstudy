from fastapi import APIRouter, Response

from app.services.export_service import build_company_export, build_ipo_export

router = APIRouter(prefix="/export", tags=["export"])

XLSX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@router.get("/ipo.xlsx")
def export_ipo_xlsx() -> Response:
    payload = build_ipo_export()
    return Response(
        content=payload,
        media_type=XLSX_MEDIA_TYPE,
        headers={"Content-Disposition": 'attachment; filename="ipo-pipeline.xlsx"'},
    )


@router.get("/company/{corp_code}.xlsx")
def export_company_xlsx(corp_code: str) -> Response:
    payload = build_company_export(corp_code)
    return Response(
        content=payload,
        media_type=XLSX_MEDIA_TYPE,
        headers={"Content-Disposition": f'attachment; filename="company-{corp_code}.xlsx"'},
    )
