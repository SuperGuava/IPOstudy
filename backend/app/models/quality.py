from sqlalchemy import Boolean, Date, DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DataQualityIssue(Base):
    __tablename__ = "data_quality_issue"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    rule_code: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(30), nullable=False)
    entity_key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    batch_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    observed_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False, server_default=func.now())


class DataQualitySummaryDaily(Base):
    __tablename__ = "data_quality_summary_daily"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    summary_date: Mapped[Date] = mapped_column(Date, nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    pass_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    warn_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    fail_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    fail_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)


class SnapshotPublishLog(Base):
    __tablename__ = "snapshot_publish_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    snapshot_type: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    entity_key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    published: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    blocked_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    batch_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    published_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False, server_default=func.now())
