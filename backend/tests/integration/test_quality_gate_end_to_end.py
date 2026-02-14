from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.db.base import Base
from app.etl.pipeline import run_pipeline
from app.models.ipo import IpoPipelineItem
from app.models.quality import SnapshotPublishLog


def test_fail_data_keeps_previous_snapshot() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        good_bundle = {
            "batch_id": "batch-good",
            "kind_rows": [
                {
                    "corp_name": "alpha-tech",
                    "market": "KOSDAQ",
                    "stage": "offering",
                    "listing_date": "2026-03-15",
                    "lead_manager": "future-securities",
                }
            ],
            "dart_rows": [
                {
                    "corp_code": "00126380",
                    "corp_name": "alpha-tech",
                    "rcept_no": "20260214000001",
                    "report_nm": "securities filing",
                    "rcept_dt": "20260214",
                }
            ],
        }
        bad_bundle = {
            "batch_id": "batch-bad",
            "kind_rows": [
                {
                    "corp_name": "alpha-tech",
                    "market": "KOSDAQ",
                    "stage": "UNKNOWN",
                    "listing_date": "2026-03-15",
                    "lead_manager": "future-securities",
                }
            ],
            "dart_rows": [
                {
                    "corp_code": "00126380",
                    "corp_name": "alpha-tech",
                    "rcept_no": "20260214000001",
                    "report_nm": "securities filing",
                    "rcept_dt": "20260214",
                }
            ],
        }

        first = run_pipeline(session, good_bundle)
        assert first.published is True
        before_count = session.execute(select(func.count(IpoPipelineItem.pipeline_id))).scalar_one()
        assert before_count == 1

        second = run_pipeline(session, bad_bundle)
        assert second.published is False
        after_count = session.execute(select(func.count(IpoPipelineItem.pipeline_id))).scalar_one()
        assert after_count == before_count

        logs = session.execute(select(SnapshotPublishLog).order_by(SnapshotPublishLog.id)).scalars().all()
        assert len(logs) == 2
        assert logs[0].published is True
        assert logs[1].published is False
