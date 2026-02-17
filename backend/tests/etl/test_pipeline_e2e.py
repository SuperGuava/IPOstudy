from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db.base import Base
from app.etl.pipeline import run_pipeline
from app.models.ipo import IpoPipelineItem


def test_pipeline_builds_ipo_item_from_kind_and_dart() -> None:
    engine = create_engine('sqlite+pysqlite:///:memory:', future=True)
    Base.metadata.create_all(engine)

    fixture_bundle = {
        'kind_rows': [
            {
                'corp_name': 'alpha-tech',
                'market': 'KOSDAQ',
                'stage': 'offering',
                'listing_date': '2026-03-15',
                'lead_manager': 'future-securities',
            }
        ],
        'dart_rows': [
            {
                'corp_code': '00126380',
                'corp_name': 'alpha-tech',
                'rcept_no': '20260214000001',
                'report_nm': 'securities filing',
                'rcept_dt': '20260214',
            }
        ],
    }

    with Session(engine) as session:
        run_pipeline(session, fixture_bundle)
        item = session.execute(select(IpoPipelineItem)).scalar_one()
        assert item.corp_code == '00126380'
        assert item.stage == 'offering'


def test_pipeline_replaces_previous_snapshot_items() -> None:
    engine = create_engine('sqlite+pysqlite:///:memory:', future=True)
    Base.metadata.create_all(engine)

    first_bundle = {
        'kind_rows': [
            {'corp_name': 'alpha', 'market': 'KOSDAQ', 'stage': 'offering', 'listing_date': '2026-03-15', 'lead_manager': 'a'},
        ],
        'dart_rows': [],
    }
    second_bundle = {
        'kind_rows': [
            {'corp_name': 'beta', 'market': 'KOSDAQ', 'stage': 'offering', 'listing_date': '2026-04-15', 'lead_manager': 'b'},
        ],
        'dart_rows': [],
    }

    with Session(engine) as session:
        run_pipeline(session, first_bundle)
        assert len(session.execute(select(IpoPipelineItem)).scalars().all()) == 1
        run_pipeline(session, second_bundle)
        rows = session.execute(select(IpoPipelineItem)).scalars().all()
        assert len(rows) == 1
        assert rows[0].corp_name == 'beta'
