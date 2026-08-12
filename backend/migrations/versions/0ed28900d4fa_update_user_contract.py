"""update_user_contract

Revision ID: 0ed28900d4fa
Revises: bbcaefb27b5f
Create Date: 2026-08-09 09:24:39.459214

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0ed28900d4fa'
down_revision: Union[str, None] = 'bbcaefb27b5f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---------------------------------------------------------
    # 1. Normalize existing role values
    # ---------------------------------------------------------
    op.execute(
        "UPDATE users "
        "SET role = 'VIEWER' "
        "WHERE role IS NULL"
    )

    # Normalize legacy lowercase values if any exist.
    op.execute(
        "UPDATE users "
        "SET role = UPPER(role) "
        "WHERE role IS NOT NULL"
    )

    op.alter_column(
        "users",
        "role",
        existing_type=sa.String(),
        nullable=False,
        server_default="VIEWER",
    )

    # ---------------------------------------------------------
    # 2. Normalize is_active before type conversion
    # ---------------------------------------------------------
    op.execute(
        "UPDATE users "
        "SET is_active = 'true' "
        "WHERE is_active IS NULL OR is_active = ''"
    )

    op.execute(
        """
        ALTER TABLE users
        ALTER COLUMN is_active TYPE BOOLEAN
        USING is_active::boolean
        """
    )

    op.alter_column(
        "users",
        "is_active",
        existing_type=sa.Boolean(),
        nullable=False,
        server_default=sa.text("true"),
    )


def downgrade() -> None:
    # ---------------------------------------------------------
    # is_active BOOLEAN -> VARCHAR
    # ---------------------------------------------------------
    op.alter_column(
        "users",
        "is_active",
        existing_type=sa.Boolean(),
        type_=sa.String(),
        nullable=True,
        server_default=None,
    )

    # ---------------------------------------------------------
    # role NOT NULL -> NULL
    # ---------------------------------------------------------
    op.alter_column(
        "users",
        "role",
        existing_type=sa.String(),
        nullable=True,
        server_default=None,
    )