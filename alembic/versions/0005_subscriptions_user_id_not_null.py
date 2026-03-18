"""make subscriptions.user_id NOT NULL (backfill from telegram_links by chat_id)

Revision ID: 0005_subscriptions_user_id_not_null
Revises: 0004_telegram_pending_phones
Create Date: 2026-03-18

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0005_subscriptions_user_id_not_null"
down_revision = "0004_telegram_pending_phones"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Backfill user_id for legacy rows where possible (chat_id match)
    op.execute(
        """
        UPDATE subscriptions s
        SET user_id = tl.user_id
        FROM telegram_links tl
        WHERE s.user_id IS NULL
          AND s.chat_id IS NOT NULL
          AND tl.chat_id = s.chat_id
        """
    )

    # Guard: fail fast if there are still rows without user_id
    conn = op.get_bind()
    remaining = conn.execute(sa.text("SELECT COUNT(*) FROM subscriptions WHERE user_id IS NULL")).scalar()
    if remaining and int(remaining) > 0:
        raise RuntimeError(
            f"Cannot set subscriptions.user_id NOT NULL: {remaining} rows still have user_id=NULL. "
            "Fix data (telegram_links/chat_id) or delete/migrate those subscriptions first."
        )

    op.alter_column("subscriptions", "user_id", existing_type=sa.Integer(), nullable=False)


def downgrade() -> None:
    op.alter_column("subscriptions", "user_id", existing_type=sa.Integer(), nullable=True)
