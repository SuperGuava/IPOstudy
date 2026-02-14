from fastapi import APIRouter

router = APIRouter(prefix="/ipo", tags=["ipo"])


@router.get("/pipeline")
def get_ipo_pipeline() -> dict:
    return {
        "items": [
            {
                "pipeline_id": "alpha-ipo-1",
                "corp_code": "00126380",
                "corp_name": "alpha-tech",
                "stage": "offering",
                "listing_date": "2026-03-15",
            }
        ]
    }


@router.get("/{pipeline_id}")
def get_ipo_detail(pipeline_id: str) -> dict:
    return {
        "pipeline_id": pipeline_id,
        "corp_code": "00126380",
        "corp_name": "alpha-tech",
        "stage": "offering",
        "listing_date": "2026-03-15",
        "lead_manager": "future-securities",
        "dart": {"rcept_no": "20260214000001"},
    }
