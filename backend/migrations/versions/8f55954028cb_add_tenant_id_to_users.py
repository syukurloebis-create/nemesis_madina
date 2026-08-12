"""add_tenant_id_to_users

Revision ID: 8f55954028cb
Revises: 4c60c838bdd2
Create Date: 2026-08-11 15:05:35.233660

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '8f55954028cb'
down_revision: Union[str, None] = '4c60c838bdd2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add tenant_id as nullable so existing users can be migrated safely.
    op.add_column(
        "users",
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )

    # 2. Backfill existing users to the canonical ITJEN tenant.
    op.execute(
        sa.text(
            """
            UPDATE users
            SET tenant_id = :tenant_id
            WHERE tenant_id IS NULL
            """
        ).bindparams(
            tenant_id="11111111-1111-1111-1111-111111111111"
        )
    )

    # 3. Enforce the mandatory tenant contract.
    op.alter_column(
        "users",
        "tenant_id",
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=False,
    )

    # 4. Enforce referential integrity.
    op.create_foreign_key(
        "fk_users_tenant_id",
        "users",
        "tenants",
        ["tenant_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_users_tenant_id",
        "users",
        type_="foreignkey",
    )
    op.drop_column("users", "tenant_id")