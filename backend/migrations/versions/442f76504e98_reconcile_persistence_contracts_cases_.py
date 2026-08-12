"""reconcile_persistence_contracts_cases_users

Revision ID: 442f76504e98
Revises: 983335c19d37
Create Date: 2026-08-08 13:31:22.219946

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '442f76504e98'
down_revision: Union[str, None] = '983335c19d37'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ============================================================
    # 1. cases.title
    # VARCHAR NULL -> VARCHAR NOT NULL
    #
    # Precondition: cases.title contains no NULL values.
    # Verified by P0-C.4 precondition check.
    # ============================================================
    op.alter_column(
        "cases",
        "title",
        existing_type=sa.String(),
        existing_nullable=True,
        nullable=False,
    )

    # ============================================================
    # 2. cases.description
    # VARCHAR -> TEXT
    #
    # PostgreSQL performs this conversion without data loss.
    # Nullability remains unchanged.
    # ============================================================
    op.alter_column(
        "cases",
        "description",
        existing_type=sa.String(),
        type_=sa.Text(),
        existing_nullable=True,
    )

    # ============================================================
    # 3. cases.created_by
    # VARCHAR -> UUID
    #
    # P0-C.1 verified that every non-null existing value is a
    # canonical UUID string.
    #
    # Explicit USING avoids relying on implicit PostgreSQL casts.
    # ============================================================
    op.alter_column(
        "cases",
        "created_by",
        existing_type=sa.String(),
        type_=sa.UUID(),
        existing_nullable=True,
        postgresql_using="created_by::uuid",
    )

    # ============================================================
    # 4. users.created_at
    # TIMESTAMP WITHOUT TIME ZONE -> TIMESTAMPTZ
    #
    # Existing values are interpreted as UTC.
    #
    # IMPORTANT:
    # This is intentional because audit timestamps are canonicalized
    # to UTC. Do not remove the explicit AT TIME ZONE expression.
    # ============================================================
    op.alter_column(
        "users",
        "created_at",
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=True,
        postgresql_using="created_at AT TIME ZONE 'UTC'",
    )


def downgrade() -> None:
    # ============================================================
    # Reverse users.created_at
    # TIMESTAMPTZ -> TIMESTAMP WITHOUT TIME ZONE
    #
    # Convert UTC-aware timestamps back to UTC wall-clock values.
    # ============================================================
    op.alter_column(
        "users",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        existing_nullable=True,
        postgresql_using="created_at AT TIME ZONE 'UTC'",
    )

    # ============================================================
    # Reverse cases.created_by
    # UUID -> VARCHAR
    # ============================================================
    op.alter_column(
        "cases",
        "created_by",
        existing_type=sa.UUID(),
        type_=sa.String(),
        existing_nullable=True,
        postgresql_using="created_by::text",
    )

    # ============================================================
    # Reverse cases.description
    # TEXT -> VARCHAR
    # ============================================================
    op.alter_column(
        "cases",
        "description",
        existing_type=sa.Text(),
        type_=sa.String(),
        existing_nullable=True,
    )

    # ============================================================
    # Reverse cases.title
    # NOT NULL -> NULLABLE
    # ============================================================
    op.alter_column(
        "cases",
        "title",
        existing_type=sa.String(),
        existing_nullable=False,
        nullable=True,
    )