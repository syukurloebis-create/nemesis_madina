"""repair assignment sla columns

Revision ID: xxxx
Revises: aff37ab5b174
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "3cf95d732fda"
down_revision: Union[str, None] = "aff37ab5b174"
branch_labels: Union[str, Sequence[str], None] = None
depends_on = None


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


def downgrade():

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
