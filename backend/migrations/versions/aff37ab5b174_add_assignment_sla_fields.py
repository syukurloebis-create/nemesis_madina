"""add assignment sla fields

Revision ID: aff37ab5b174
Revises: f5f2597047f2
Create Date: 2026-06-28
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "aff37ab5b174"
down_revision: Union[str, None] = "f5f2597047f2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.add_column(
        "finding_assignments",
        sa.Column(
            "assigned_at",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.add_column(
        "finding_assignments",
        sa.Column(
            "sla_due_at",
            sa.TIMESTAMP(),
            nullable=True,
        ),
    )

    op.add_column(
        "finding_assignments",
        sa.Column(
            "completed_at",
            sa.TIMESTAMP(),
            nullable=True,
        ),
    )

    op.add_column(
        "finding_assignments",
        sa.Column(
            "priority",
            sa.String(50),
            server_default="NORMAL",
            nullable=False,
        ),
    )

    op.create_index(
        "idx_assignment_sla_due",
        "finding_assignments",
        ["sla_due_at"],
    )


def downgrade() -> None:

    op.drop_index(
        "idx_assignment_sla_due",
        table_name="finding_assignments",
    )

    op.drop_column(
        "finding_assignments",
        "priority",
    )

    op.drop_column(
        "finding_assignments",
        "completed_at",
    )

    op.drop_column(
        "finding_assignments",
        "sla_due_at",
    )

    op.drop_column(
        "finding_assignments",
        "assigned_at",
    )
