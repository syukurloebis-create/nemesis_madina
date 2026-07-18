"""add finding assignments table

Revision ID: 7e54d7e
Revises: 320c2458b5e1
Create Date: 2026-06-28
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "7e54d7e"
down_revision: Union[str, None] = "320c2458b5e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.create_table(
        "finding_assignments",

        sa.Column(
            "id",
            postgresql.UUID(),
            server_default=sa.text(
                "gen_random_uuid()"
            ),
            nullable=False,
        ),

        sa.Column(
            "finding_id",
            sa.String(),
            nullable=False,
        ),

        sa.Column(
            "analyst_id",
            sa.String(100),
            nullable=True,
        ),

        sa.Column(
            "analyst_name",
            sa.String(200),
            nullable=False,
        ),

        sa.Column(
            "assigned_by",
            sa.String(100),
            nullable=True,
        ),

        sa.Column(
            "role",
            sa.String(100),
            nullable=True,
        ),

        sa.Column(
            "status",
            sa.String(50),
            server_default="ACTIVE",
            nullable=False,
        ),

        sa.Column(
            "notes",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text(
                "now()"
            ),
            nullable=True,
        ),

        sa.Column(
            "closed_at",
            sa.TIMESTAMP(),
            nullable=True,
        ),

        sa.PrimaryKeyConstraint(
            "id"
        ),
    )


    op.create_index(
        "idx_finding_assignment_finding",
        "finding_assignments",
        [
            "finding_id"
        ],
    )


def downgrade() -> None:

    op.drop_index(
        "idx_finding_assignment_finding",
        table_name="finding_assignments",
    )

    op.drop_table(
        "finding_assignments",
    )