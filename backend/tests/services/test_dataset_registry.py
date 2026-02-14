import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.base import Base
from app.models.snapshot import DatasetRegistry
from app.services.dataset_registry_service import DatasetRegistryService


@pytest.fixture()
def db_session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_get_dataset_returns_row(db_session: Session) -> None:
    db_session.add(
        DatasetRegistry(
            dataset_key="stock.marketcap",
            bld="dbms/MDC/STAT/standard/MDCSTAT01501",
        )
    )
    db_session.commit()

    service = DatasetRegistryService(session=db_session)
    row = service.get_dataset("stock.marketcap")
    assert row.dataset_key == "stock.marketcap"
    assert row.bld.endswith("MDCSTAT01501")


def test_get_dataset_raises_for_missing_key(db_session: Session) -> None:
    service = DatasetRegistryService(session=db_session)
    with pytest.raises(KeyError):
        service.get_dataset("missing.key")
