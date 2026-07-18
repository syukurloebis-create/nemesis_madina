"""add metadata to finding events

Revision ID: 5145313e9e12
Revises: 721b0926d105
Create Date: 2026-06-28
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "5145313e9e12"
down_revision: Union[str, None] = "721b0926d105"
branch_labels = None
depends_on = None


def upgrade() -> None:

    op.add_column(
        "finding_events",
        sa.Column(
            "metadata",
            sa.JSON(),
            nullable=True,
        ),
    )


def downgrade() -> None:

    op.drop_column(
        "finding_events",
        "metadata",
    )
