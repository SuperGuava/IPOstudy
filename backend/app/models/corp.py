from sqlalchemy import Date, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CorpMaster(Base):
    __tablename__ = "corp_master"

    corp_code: Mapped[str] = mapped_column(String(8), primary_key=True)
    stock_code: Mapped[str | None] = mapped_column(String(6), nullable=True)
    corp_name: Mapped[str] = mapped_column(String(255), nullable=False)
    eng_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    modify_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    market_cls: Mapped[str | None] = mapped_column(String(20), nullable=True)


class CorpProfile(Base):
    __tablename__ = "corp_profile"

    corp_code: Mapped[str] = mapped_column(String(8), primary_key=True)
    ceo_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    industry_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    fiscal_month: Mapped[str | None] = mapped_column(String(2), nullable=True)
    homepage_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
