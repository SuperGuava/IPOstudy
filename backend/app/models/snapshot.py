from sqlalchemy import JSON, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CompanySnapshot(Base):
    __tablename__ = "company_snapshot"

    corp_code: Mapped[str] = mapped_column(String(8), primary_key=True)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False, server_default=func.now())


class IpoPipelineSnapshot(Base):
    __tablename__ = "ipo_pipeline_snapshot"

    snapshot_date: Mapped[str] = mapped_column(String(10), primary_key=True)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False, server_default=func.now())


class DatasetRegistry(Base):
    __tablename__ = "dataset_registry"

    dataset_key: Mapped[str] = mapped_column(String(100), primary_key=True)
    bld: Mapped[str] = mapped_column(String(255), nullable=False)
    required_params: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    market_scope: Mapped[str | None] = mapped_column(String(20), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sample_response_schema: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class RawPayloadLog(Base):
    __tablename__ = "raw_payload_log"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String(20), nullable=False)
    endpoint: Mapped[str] = mapped_column(String(255), nullable=False)
    request_key: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    payload: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False, server_default=func.now())
