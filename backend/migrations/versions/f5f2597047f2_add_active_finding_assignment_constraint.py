"""add active finding assignment constraint

Revision ID: f5f2597047f2
Revises: 7e54d7e
"""

from typing import Sequence, Union

from alembic import op


revision: str = "f5f2597047f2"
down_revision: Union[str, None] = "7e54d7e"

branch_labels = None
depends_on = None


def upgrade() -> None:

    op.create_index(
        "uq_active_finding_assignment",
        "finding_assignments",
        ["finding_id"],
        unique=True,
        postgresql_where=(
            "status='ACTIVE'"
        ),
    )


def downgrade() -> None:

    op.drop_index(
        "uq_active_finding_assignment",
        table_name="finding_assignments",
    )