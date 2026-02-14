from sqlalchemy import JSON, Date, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class IpoPipelineItem(Base):
    __tablename__ = "ipo_pipeline_item"

    pipeline_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    corp_name: Mapped[str] = mapped_column(String(255), nullable=False)
    corp_code: Mapped[str | None] = mapped_column(String(8), nullable=True, index=True)
    expected_stock_code: Mapped[str | None] = mapped_column(String(6), nullable=True)
    stage: Mapped[str] = mapped_column(String(30), nullable=False)
    key_dates: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    offer_price: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    offer_amount: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    lead_manager: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_kind_row_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    source_dart_rcept_no: Mapped[str | None] = mapped_column(String(20), nullable=True)
    listing_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
