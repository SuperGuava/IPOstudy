"""add quality tables

Revision ID: 20260214_02
Revises: 20260214_01
Create Date: 2026-02-14
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260214_02"
down_revision: str | None = "20260214_01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "data_quality_issue",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("source", sa.String(length=20), nullable=False),
        sa.Column("rule_code", sa.String(length=100), nullable=False),
        sa.Column("severity", sa.String(length=10), nullable=False),
        sa.Column("entity_type", sa.String(length=30), nullable=False),
        sa.Column("entity_key", sa.String(length=100), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("batch_id", sa.String(length=64), nullable=True),
        sa.Column("observed_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_data_quality_issue_source", "data_quality_issue", ["source"])
    op.create_index("ix_data_quality_issue_rule_code", "data_quality_issue", ["rule_code"])
    op.create_index("ix_data_quality_issue_severity", "data_quality_issue", ["severity"])
    op.create_index("ix_data_quality_issue_entity_key", "data_quality_issue", ["entity_key"])
    op.create_index("ix_data_quality_issue_batch_id", "data_quality_issue", ["batch_id"])

    op.create_table(
        "data_quality_summary_daily",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("summary_date", sa.Date(), nullable=False),
        sa.Column("source", sa.String(length=20), nullable=False),
        sa.Column("pass_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("warn_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("fail_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("fail_rate", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_data_quality_summary_daily_summary_date",
        "data_quality_summary_daily",
        ["summary_date"],
    )
    op.create_index("ix_data_quality_summary_daily_source", "data_quality_summary_daily", ["source"])

    op.create_table(
        "snapshot_publish_log",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("snapshot_type", sa.String(length=30), nullable=False),
        sa.Column("entity_key", sa.String(length=100), nullable=False),
        sa.Column("published", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("blocked_reason", sa.Text(), nullable=True),
        sa.Column("batch_id", sa.String(length=64), nullable=True),
        sa.Column("published_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_snapshot_publish_log_snapshot_type", "snapshot_publish_log", ["snapshot_type"])
    op.create_index("ix_snapshot_publish_log_entity_key", "snapshot_publish_log", ["entity_key"])
    op.create_index("ix_snapshot_publish_log_batch_id", "snapshot_publish_log", ["batch_id"])


def downgrade() -> None:
    op.drop_index("ix_snapshot_publish_log_batch_id", table_name="snapshot_publish_log")
    op.drop_index("ix_snapshot_publish_log_entity_key", table_name="snapshot_publish_log")
    op.drop_index("ix_snapshot_publish_log_snapshot_type", table_name="snapshot_publish_log")
    op.drop_table("snapshot_publish_log")

    op.drop_index("ix_data_quality_summary_daily_source", table_name="data_quality_summary_daily")
    op.drop_index("ix_data_quality_summary_daily_summary_date", table_name="data_quality_summary_daily")
    op.drop_table("data_quality_summary_daily")

    op.drop_index("ix_data_quality_issue_batch_id", table_name="data_quality_issue")
    op.drop_index("ix_data_quality_issue_entity_key", table_name="data_quality_issue")
    op.drop_index("ix_data_quality_issue_severity", table_name="data_quality_issue")
    op.drop_index("ix_data_quality_issue_rule_code", table_name="data_quality_issue")
    op.drop_index("ix_data_quality_issue_source", table_name="data_quality_issue")
    op.drop_table("data_quality_issue")
