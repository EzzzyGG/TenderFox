"""make subscriptions.user_id NOT NULL (backfill from telegram_links by chat_id)

Revision ID: 0005_subscriptions_user_id_not_null
Revises: 0004_telegram_pending_phones
Create Date: 2026-03-18

"""

from __future__ import annotations

from alembic import op


# revision identifiers, used by Alembic.
revision = "0005_subscriptions_user_id_not_null"
down_revision = "0004_telegram_pending_phones"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Backfill user_id for legacy subscriptions created before user_id migration
    op.execute(
        """
        UPDATE subscriptions s
        SET user_id = tl.user_id
        FROM telegram_links tl
        WHERE s.user_id IS NULL
          AND s.chat_id = tl.chat_id
          AND tl.user_id IS NOT NULL
        """
    )

    op.execute("ALTER TABLE subscriptions ALTER COLUMN user_id SET NOT NULL")


def downgrade() -> None:
    op.execute("ALTER TABLE subscriptions ALTER COLUMN user_id DROP NOT NULL")
