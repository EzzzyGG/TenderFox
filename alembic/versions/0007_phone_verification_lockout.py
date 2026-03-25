"""add lockout fields to phone_verifications

Revision ID: 0007_phone_verification_lockout
Revises: 0006_drop_subscriptions_chat_id
Create Date: 2026-03-25

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0007_phone_verification_lockout"
down_revision = "0006_drop_subscriptions_chat_id"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "phone_verifications",
        sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("phone_verifications", "locked_until")
