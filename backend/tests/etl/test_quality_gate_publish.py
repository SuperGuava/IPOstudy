from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db.base import Base
from app.etl.pipeline import run_pipeline
from app.models.ipo import IpoPipelineItem
from app.models.quality import SnapshotPublishLog


def test_fail_issue_blocks_snapshot_publish() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    fixture_bundle = {
        "batch_id": "batch-fail-1",
        "kind_rows": [
            {
                "corp_name": "알파테크",
                "market": "KOSDAQ",
                "stage": "UNKNOWN",
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
        result = run_pipeline(session, fixture_bundle)
        assert result.published is False
        assert session.execute(select(IpoPipelineItem)).all() == []
        log = session.execute(select(SnapshotPublishLog)).scalar_one()
        assert log.published is False


def test_warn_issue_allows_snapshot_publish() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    fixture_bundle = {
        "batch_id": "batch-warn-1",
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
                "report_nm": "",
                "rcept_dt": "20260214",
            }
        ],
    }
    with Session(engine) as session:
        result = run_pipeline(session, fixture_bundle)
        assert result.published is True
        assert session.execute(select(IpoPipelineItem)).all()
