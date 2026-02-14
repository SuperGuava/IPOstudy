import json
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.connectors.krx_connector import KrxConnector
from app.db.base import Base
from app.models.snapshot import DatasetRegistry
from app.services.dataset_registry_service import DatasetRegistryService


FIXTURE_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "krx" / "marketcap_response.json"


class FakeKrxClient:
    def __init__(self) -> None:
        self.last_url: str | None = None
        self.last_data: dict | None = None

    def post_json(self, url: str, data: dict) -> dict:
        self.last_url = url
        self.last_data = data
        return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


@pytest.fixture()
def db_session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_krx_connector_uses_registry_bld(db_session: Session) -> None:
    fake_http = FakeKrxClient()
    db_session.add(
        DatasetRegistry(
            dataset_key="stock.marketcap",
            bld="dbms/MDC/STAT/standard/MDCSTAT01501",
            required_params={"trdDd": "required"},
        )
    )
    db_session.commit()

    connector = KrxConnector(http_client=fake_http)
    registry = DatasetRegistryService(session=db_session)
    data = registry.fetch_dataset(
        "stock.marketcap",
        {"trdDd": "20260213"},
        connector=connector,
    )

    assert "OutBlock_1" in data
    assert fake_http.last_data is not None
    assert fake_http.last_data["bld"] == "dbms/MDC/STAT/standard/MDCSTAT01501"
