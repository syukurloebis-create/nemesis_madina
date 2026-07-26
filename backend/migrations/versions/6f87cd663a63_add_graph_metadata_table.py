"""add_graph_metadata_table

Revision ID: 6f87cd663a63
Revises: 3d94f136531d
Create Date: 2026-07-24 08:39:43.640833

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6f87cd663a63'
down_revision: Union[str, None] = '3d94f136531d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "graph_metadata",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("case_id", sa.String(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("checksum", sa.String(), nullable=False),
        sa.Column("reason", sa.String(), nullable=True),
        sa.Column(
            "regenerated_by",
            sa.String(),
            nullable=True,
            server_default="system",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_index(
        "idx_graph_metadata_case_id",
        "graph_metadata",
        ["case_id"],
        unique=False,
    )

    op.create_index(
        "idx_graph_metadata_version",
        "graph_metadata",
        ["version"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "idx_graph_metadata_version",
        table_name="graph_metadata",
    )

    op.drop_index(
        "idx_graph_metadata_case_id",
        table_name="graph_metadata",
    )

    op.drop_table("graph_metadata")
