from sqlalchemy import Boolean, Date, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DartDisclosure(Base):
    __tablename__ = "dart_disclosure"

    rcept_no: Mapped[str] = mapped_column(String(20), primary_key=True)
    corp_code: Mapped[str] = mapped_column(String(8), nullable=False, index=True)
    report_nm: Mapped[str] = mapped_column(String(255), nullable=False)
    rcept_dt: Mapped[Date | None] = mapped_column(Date, nullable=True)
    flr_nm: Mapped[str | None] = mapped_column(String(255), nullable=True)
    pblntf_ty: Mapped[str | None] = mapped_column(String(10), nullable=True)
    pblntf_detail_ty: Mapped[str | None] = mapped_column(String(10), nullable=True)
    is_final: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_amended: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
