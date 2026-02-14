from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db.base import Base
from app.etl.pipeline import run_pipeline
from app.models.ipo import IpoPipelineItem


def test_pipeline_builds_ipo_item_from_kind_and_dart() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    fixture_bundle = {
        "kind_rows": [
            {
                "corp_name": "알파테크",
                "market": "KOSDAQ",
                "stage": "공모",
                "listing_date": "2026-03-15",
                "lead_manager": "미래증권",
            }
        ],
        "dart_rows": [
            {
                "corp_code": "00126380",
                "corp_name": "알파테크",
                "rcept_no": "20260214000001",
                "report_nm": "증권신고서(지분증권)",
                "rcept_dt": "20260214",
            }
        ],
    }

    with Session(engine) as session:
        run_pipeline(session, fixture_bundle)
        item = session.execute(select(IpoPipelineItem)).scalar_one()
        assert item.corp_code is not None
        assert item.stage in {"예비심사", "공모", "상장예정", "신규상장"}
