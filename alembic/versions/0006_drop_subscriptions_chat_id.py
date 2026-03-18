"""drop legacy subscriptions.chat_id

Revision ID: 0006_drop_subscriptions_chat_id
Revises: 0005_subscriptions_user_id_not_null
Create Date: 2026-03-18

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0006_drop_subscriptions_chat_id"
down_revision = "0005_subscriptions_user_id_not_null"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index("ix_subscriptions_chat_id", table_name="subscriptions")
    op.drop_column("subscriptions", "chat_id")


def downgrade() -> None:
    op.add_column("subscriptions", sa.Column("chat_id", sa.String(length=64), nullable=True))
    op.create_index("ix_subscriptions_chat_id", "subscriptions", ["chat_id"], unique=False)
