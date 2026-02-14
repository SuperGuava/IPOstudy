"""init schema

Revision ID: 20260214_01
Revises:
Create Date: 2026-02-14
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260214_01"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "corp_master",
        sa.Column("corp_code", sa.String(length=8), nullable=False),
        sa.Column("stock_code", sa.String(length=6), nullable=True),
        sa.Column("corp_name", sa.String(length=255), nullable=False),
        sa.Column("eng_name", sa.String(length=255), nullable=True),
        sa.Column("modify_date", sa.Date(), nullable=True),
        sa.Column("market_cls", sa.String(length=20), nullable=True),
        sa.PrimaryKeyConstraint("corp_code"),
    )
    op.create_table(
        "corp_profile",
        sa.Column("corp_code", sa.String(length=8), nullable=False),
        sa.Column("ceo_name", sa.String(length=255), nullable=True),
        sa.Column("industry_code", sa.String(length=20), nullable=True),
        sa.Column("fiscal_month", sa.String(length=2), nullable=True),
        sa.Column("homepage_url", sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint("corp_code"),
    )
    op.create_table(
        "dart_disclosure",
        sa.Column("rcept_no", sa.String(length=20), nullable=False),
        sa.Column("corp_code", sa.String(length=8), nullable=False),
        sa.Column("report_nm", sa.String(length=255), nullable=False),
        sa.Column("rcept_dt", sa.Date(), nullable=True),
        sa.Column("flr_nm", sa.String(length=255), nullable=True),
        sa.Column("pblntf_ty", sa.String(length=10), nullable=True),
        sa.Column("pblntf_detail_ty", sa.String(length=10), nullable=True),
        sa.Column("is_final", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_amended", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.PrimaryKeyConstraint("rcept_no"),
    )
    op.create_index("ix_dart_disclosure_corp_code", "dart_disclosure", ["corp_code"])

    op.create_table(
        "ipo_pipeline_item",
        sa.Column("pipeline_id", sa.String(length=64), nullable=False),
        sa.Column("corp_name", sa.String(length=255), nullable=False),
        sa.Column("corp_code", sa.String(length=8), nullable=True),
        sa.Column("expected_stock_code", sa.String(length=6), nullable=True),
        sa.Column("stage", sa.String(length=30), nullable=False),
        sa.Column("key_dates", sa.JSON(), nullable=True),
        sa.Column("offer_price", sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column("offer_amount", sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column("lead_manager", sa.String(length=255), nullable=True),
        sa.Column("source_kind_row_id", sa.String(length=64), nullable=True),
        sa.Column("source_dart_rcept_no", sa.String(length=20), nullable=True),
        sa.Column("listing_date", sa.Date(), nullable=True),
        sa.PrimaryKeyConstraint("pipeline_id"),
    )
    op.create_index("ix_ipo_pipeline_item_corp_code", "ipo_pipeline_item", ["corp_code"])

    op.create_table(
        "company_snapshot",
        sa.Column("corp_code", sa.String(length=8), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("corp_code"),
    )
    op.create_table(
        "ipo_pipeline_snapshot",
        sa.Column("snapshot_date", sa.String(length=10), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("snapshot_date"),
    )
    op.create_table(
        "dataset_registry",
        sa.Column("dataset_key", sa.String(length=100), nullable=False),
        sa.Column("bld", sa.String(length=255), nullable=False),
        sa.Column("required_params", sa.JSON(), nullable=True),
        sa.Column("market_scope", sa.String(length=20), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("sample_response_schema", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("dataset_key"),
    )
    op.create_table(
        "raw_payload_log",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("source", sa.String(length=20), nullable=False),
        sa.Column("endpoint", sa.String(length=255), nullable=False),
        sa.Column("request_key", sa.String(length=255), nullable=True),
        sa.Column("payload", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_raw_payload_log_request_key", "raw_payload_log", ["request_key"])


def downgrade() -> None:
    op.drop_index("ix_raw_payload_log_request_key", table_name="raw_payload_log")
    op.drop_table("raw_payload_log")
    op.drop_table("dataset_registry")
    op.drop_table("ipo_pipeline_snapshot")
    op.drop_table("company_snapshot")
    op.drop_index("ix_ipo_pipeline_item_corp_code", table_name="ipo_pipeline_item")
    op.drop_table("ipo_pipeline_item")
    op.drop_index("ix_dart_disclosure_corp_code", table_name="dart_disclosure")
    op.drop_table("dart_disclosure")
    op.drop_table("corp_profile")
    op.drop_table("corp_master")
