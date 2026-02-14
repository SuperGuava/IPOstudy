from fastapi import APIRouter

from app.services.snapshot_service import build_company_snapshot

router = APIRouter(prefix="/company", tags=["company"])


@router.get("/snapshot")
def get_company_snapshot(corp_code: str) -> dict:
    snapshot = build_company_snapshot(
        corp_code=corp_code,
        payload={
            "profile": {"corp_name": "알파테크", "corp_code": corp_code},
            "disclosures": [],
            "financials": {"year": 2025, "revenue": 1000000000},
            "market": {"market_cap": 423849000000000},
        },
    )
    return {
        "corp_code": snapshot.corp_code,
        "partial": snapshot.partial,
        "source_status": snapshot.source_status,
        "missing_sections": snapshot.missing_sections,
        "profile": snapshot.profile,
        "disclosures": snapshot.disclosures,
        "financials": snapshot.financials,
        "market": snapshot.market,
    }


@router.get("/{corp_code}/financials")
def get_company_financials(corp_code: str) -> dict:
    return {
        "corp_code": corp_code,
        "financials": {
            "annual": [
                {"year": 2023, "revenue": 900000000, "net_income": 120000000},
                {"year": 2024, "revenue": 980000000, "net_income": 130000000},
                {"year": 2025, "revenue": 1000000000, "net_income": 140000000},
            ]
        },
    }
