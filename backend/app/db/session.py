import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.url import normalize_database_url

DATABASE_URL = normalize_database_url(
    os.getenv("DATABASE_URL"),
    default="sqlite:///./anti_gravity.db",
)

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
