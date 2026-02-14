from datetime import datetime

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db.base import Base
from app.jobs.tasks import run_quality_summary_job
from app.models.quality import DataQualityIssue, DataQualitySummaryDaily


def test_quality_summary_job_writes_daily_rows() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.add_all(
            [
                DataQualityIssue(
                    source="DART",
                    rule_code="DART_RCEPT_NO_FORMAT",
                    severity="FAIL",
                    entity_type="disclosure",
                    entity_key="00126380",
                    message="bad format",
                    batch_id="b1",
                    observed_at=datetime(2026, 2, 14, 1, 0, 0),
                ),
                DataQualityIssue(
                    source="DART",
                    rule_code="DART_REPORT_NAME_EMPTY",
                    severity="WARN",
                    entity_type="disclosure",
                    entity_key="00126380",
                    message="empty",
                    batch_id="b1",
                    observed_at=datetime(2026, 2, 14, 2, 0, 0),
                ),
            ]
        )
        session.commit()

        run_quality_summary_job(session, "2026-02-14")
        rows = session.execute(select(DataQualitySummaryDaily)).scalars().all()
        assert rows
        assert rows[0].source == "DART"
        assert rows[0].fail_count == 1
