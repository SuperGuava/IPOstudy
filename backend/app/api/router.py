from fastapi import APIRouter

from app.api.endpoints.company import router as company_router
from app.api.endpoints.export import router as export_router
from app.api.endpoints.ipo import router as ipo_router

api_router = APIRouter()


@api_router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


api_router.include_router(company_router)
api_router.include_router(ipo_router)
api_router.include_router(export_router)
