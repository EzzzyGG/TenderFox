"""telegram pending phones for bot verify flow

Revision ID: 0004_telegram_pending_phones
Revises: 0003_subscriptions_user
Create Date: 2026-03-18

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0004_telegram_pending_phones"
down_revision = "0003_subscriptions_user"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "telegram_pending_phones",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("chat_id", sa.String(length=64), nullable=False),
        sa.Column("telegram_user_id", sa.String(length=64), nullable=False),
        sa.Column("phone_e164", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.create_index("ix_telegram_pending_phones_chat_id", "telegram_pending_phones", ["chat_id"], unique=False)
    op.create_index(
        "ix_telegram_pending_phones_tg_user_id",
        "telegram_pending_phones",
        ["telegram_user_id"],
        unique=False,
    )
    op.create_index(
        "ix_telegram_pending_phones_expires_at",
        "telegram_pending_phones",
        ["expires_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_telegram_pending_phones_expires_at", table_name="telegram_pending_phones")
    op.drop_index("ix_telegram_pending_phones_tg_user_id", table_name="telegram_pending_phones")
    op.drop_index("ix_telegram_pending_phones_chat_id", table_name="telegram_pending_phones")
    op.drop_table("telegram_pending_phones")
