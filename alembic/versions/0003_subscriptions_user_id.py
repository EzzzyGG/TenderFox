"""add subscriptions.user_id (keep legacy chat_id)

Revision ID: 0003_subscriptions_user
Revises: 0002_users_auth
Create Date: 2026-03-18

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0003_subscriptions_user"
down_revision = "0002_users_auth"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("subscriptions", sa.Column("user_id", sa.Integer(), nullable=True))
    op.create_index("ix_subscriptions_user_id", "subscriptions", ["user_id"], unique=False)
    op.create_foreign_key(
        "fk_subscriptions_user_id_users",
        "subscriptions",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # keep legacy chat_id, but allow nulls
    op.alter_column("subscriptions", "chat_id", existing_type=sa.String(length=64), nullable=True)


def downgrade() -> None:
    op.alter_column("subscriptions", "chat_id", existing_type=sa.String(length=64), nullable=False)

    op.drop_constraint("fk_subscriptions_user_id_users", "subscriptions", type_="foreignkey")
    op.drop_index("ix_subscriptions_user_id", table_name="subscriptions")
    op.drop_column("subscriptions", "user_id")
