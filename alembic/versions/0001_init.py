"""init schema

Revision ID: 0001_init
Revises: 
Create Date: 2026-03-13

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tenders",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("source", sa.String(length=50), nullable=False),
        sa.Column("source_id", sa.String(length=200), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("price", sa.Numeric(18, 2), nullable=True),
        sa.Column("currency", sa.String(length=10), nullable=True),
        sa.Column("region", sa.String(length=100), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deadline_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("url", sa.Text(), nullable=True),
        sa.Column("raw_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_tenders_source_source_id", "tenders", ["source", "source_id"], unique=True)

    op.create_table(
        "subscriptions",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("chat_id", sa.String(length=64), nullable=False),
        sa.Column("keyword", sa.String(length=200), nullable=False),
        sa.Column("region", sa.String(length=100), nullable=True),
        sa.Column("min_price", sa.Numeric(18, 2), nullable=True),
        sa.Column("active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_subscriptions_chat_id", "subscriptions", ["chat_id"], unique=False)

    op.create_table(
        "deliveries",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("subscription_id", sa.BigInteger(), sa.ForeignKey("subscriptions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("tender_id", sa.BigInteger(), sa.ForeignKey("tenders.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default=sa.text("'queued'")),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index(
        "ix_deliveries_subscription_tender",
        "deliveries",
        ["subscription_id", "tender_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_deliveries_subscription_tender", table_name="deliveries")
    op.drop_table("deliveries")

    op.drop_index("ix_subscriptions_chat_id", table_name="subscriptions")
    op.drop_table("subscriptions")

    op.drop_index("ix_tenders_source_source_id", table_name="tenders")
    op.drop_table("tenders")
