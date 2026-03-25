"""drop legacy subscriptions.chat_id

Revision ID: 0006_drop_subscriptions_chat_id
Revises: 0005_subscriptions_user_id_not_null
Create Date: 2026-03-18

"""

from __future__ import annotations

from alembic import op


# revision identifiers, used by Alembic.
revision = "0006_drop_subscriptions_chat_id"
down_revision = "0005_subscriptions_user_id_not_null"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE subscriptions DROP COLUMN chat_id")


def downgrade() -> None:
    op.execute("ALTER TABLE subscriptions ADD COLUMN chat_id BIGINT")
