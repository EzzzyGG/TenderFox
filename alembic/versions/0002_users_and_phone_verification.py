"""users + phone verification + telegram links

Revision ID: 0002_users_auth
Revises: 0001_init
Create Date: 2026-03-18

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0002_users_auth"
down_revision = "0001_init"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("phone_e164", sa.String(length=32), nullable=False),
        sa.Column("phone_verified", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("phone_verified_via", sa.String(length=32), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_users_phone_e164", "users", ["phone_e164"], unique=True)

    op.create_table(
        "phone_verifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("phone_e164", sa.String(length=32), nullable=False),
        sa.Column("code", sa.String(length=16), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("used", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_phone_verifications_phone_e164", "phone_verifications", ["phone_e164"], unique=False)

    op.create_table(
        "telegram_links",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("telegram_user_id", sa.String(length=64), nullable=False),
        sa.Column("chat_id", sa.String(length=64), nullable=False),
        sa.Column("phone_e164_from_telegram", sa.String(length=32), nullable=True),
        sa.Column("linked_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_telegram_links_user_id", "telegram_links", ["user_id"], unique=True)
    op.create_unique_constraint("uq_telegram_links_tg_user", "telegram_links", ["telegram_user_id"])


def downgrade() -> None:
    op.drop_constraint("uq_telegram_links_tg_user", "telegram_links", type_="unique")
    op.drop_index("ix_telegram_links_user_id", table_name="telegram_links")
    op.drop_table("telegram_links")

    op.drop_index("ix_phone_verifications_phone_e164", table_name="phone_verifications")
    op.drop_table("phone_verifications")

    op.drop_index("ix_users_phone_e164", table_name="users")
    op.drop_table("users")
