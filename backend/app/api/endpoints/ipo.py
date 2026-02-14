from fastapi import APIRouter

router = APIRouter(prefix="/ipo", tags=["ipo"])


@router.get("/pipeline")
def get_ipo_pipeline() -> dict:
    return {
        "items": [
            {
                "pipeline_id": "alpha-ipo-1",
                "corp_name": "알파테크",
                "stage": "공모",
                "listing_date": "2026-03-15",
            }
        ]
    }


@router.get("/{pipeline_id}")
def get_ipo_detail(pipeline_id: str) -> dict:
    return {
        "pipeline_id": pipeline_id,
        "corp_name": "알파테크",
        "stage": "공모",
        "listing_date": "2026-03-15",
        "lead_manager": "미래증권",
        "dart": {"rcept_no": "20260214000001"},
    }
