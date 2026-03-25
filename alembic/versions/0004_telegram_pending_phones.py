"""telegram pending phones for bot verify flow

Revision ID: 0004_telegram_pending_phones
Revises: 0003_subscriptions_user_id
Create Date: 2026-03-18

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0004_telegram_pending_phones"
down_revision = "0003_subscriptions_user_id"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "telegram_pending_phones",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("phone_e164", sa.String(length=32), nullable=False),
        sa.Column("telegram_user_id", sa.BigInteger(), nullable=True),
        sa.Column("chat_id", sa.BigInteger(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index(
        "ix_telegram_pending_phones_phone_e164",
        "telegram_pending_phones",
        ["phone_e164"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_telegram_pending_phones_phone_e164", table_name="telegram_pending_phones")
    op.drop_table("telegram_pending_phones")
