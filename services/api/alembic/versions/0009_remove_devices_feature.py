"""Remove devices table after deprecating device management.

Revision ID: 0009
Revises: 0008
Create Date: 2026-04-27
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0009"
down_revision: Union[str, None] = "0008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_devices_token_hash")
    op.execute("DROP INDEX IF EXISTS ix_devices_user_id")
    op.execute("DROP INDEX IF EXISTS ix_devices_id")
    op.execute("DROP TABLE IF EXISTS devices")


def downgrade() -> None:
    op.create_table(
        "devices",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("device_name", sa.String(255), nullable=False, server_default=""),
        sa.Column("device_info", sa.Text(), nullable=True),
        sa.Column("token_hash", sa.String(64), nullable=False),
        sa.Column("last_active", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index(op.f("ix_devices_id"), "devices", ["id"])
    op.create_index(op.f("ix_devices_user_id"), "devices", ["user_id"])
    op.create_index(op.f("ix_devices_token_hash"), "devices", ["token_hash"], unique=True)
