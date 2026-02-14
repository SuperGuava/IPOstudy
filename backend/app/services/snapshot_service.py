from app.schemas.snapshot import CompanySnapshotResponse
from app.services.source_status_service import build_source_status


def build_company_snapshot(
    corp_code: str,
    payload: dict | None = None,
    *,
    dart_failed: bool = False,
    kind_failed: bool = False,
    krx_failed: bool = False,
) -> CompanySnapshotResponse:
    source_status = build_source_status(
        dart_failed=dart_failed,
        kind_failed=kind_failed,
        krx_failed=krx_failed,
    )
    missing_sections: list[str] = []
    if source_status["krx_market"] == "failed":
        missing_sections.append("krx_market")
    if source_status["dart"] == "failed":
        missing_sections.append("disclosures")
        missing_sections.append("financials")

    data = payload or {}
    return CompanySnapshotResponse(
        corp_code=corp_code,
        partial=bool(missing_sections),
        source_status=source_status,
        missing_sections=missing_sections,
        profile=data.get("profile", {}),
        disclosures=data.get("disclosures", []),
        financials=data.get("financials", {}),
        market=data.get("market", {}),
    )
