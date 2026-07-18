"""add finding action logs

Revision ID: 50990552f7ee
Revises: xxxx
Create Date: 2026-06-28 05:17:57.350706

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "50990552f7ee"
down_revision: Union[str, None] = "3cf95d732fda"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.create_table(
        "finding_action_logs",

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
            "assignment_id",
            postgresql.UUID(),
            nullable=True,
        ),

        sa.Column(
            "action_type",
            sa.String(100),
            nullable=False,
        ),

        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "actor_id",
            sa.String(100),
            nullable=True,
        ),

        sa.Column(
            "actor_name",
            sa.String(200),
            nullable=True,
        ),

        sa.Column(
            "actor_role",
            sa.String(100),
            nullable=True,
        ),

        sa.Column(
            "metadata",
            sa.JSON(),
            nullable=True,
        ),

        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text(
                "now()"
            ),
            nullable=False,
        ),

        sa.PrimaryKeyConstraint(
            "id"
        ),
    )


    op.create_index(
        "idx_action_logs_finding",
        "finding_action_logs",
        [
            "finding_id"
        ],
    )


    op.create_index(
        "idx_action_logs_type",
        "finding_action_logs",
        [
            "action_type"
        ],
    )


def downgrade() -> None:

    op.drop_index(
        "idx_action_logs_type",
        table_name="finding_action_logs",
    )

    op.drop_index(
        "idx_action_logs_finding",
        table_name="finding_action_logs",
    )

    op.drop_table(
        "finding_action_logs",
    )