import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


@pytest.fixture()
def db_engine() -> Engine:
    database_url = os.getenv("DATABASE_URL", "sqlite:///./anti_gravity.db")
    engine = create_engine(database_url, future=True)
    try:
        yield engine
    finally:
        engine.dispose()
