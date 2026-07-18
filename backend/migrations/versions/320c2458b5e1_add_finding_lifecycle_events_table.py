"""add finding lifecycle events table

Revision ID: 320c2458b5e1
Revises: 4cc8a0a5030b
Create Date: 2026-06-27 11:22:57.989611

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "320c2458b5e1"
down_revision: Union[str, None] = "4cc8a0a5030b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on = None


finding_status_enum = postgresql.ENUM(
    name="findingstatus",
    create_type=False
)


def upgrade() -> None:

    op.create_table(
        "finding_events",

        sa.Column(
            "id",
            postgresql.UUID(),
            server_default=sa.text(
                "gen_random_uuid()"
            ),
            nullable=False
        ),

        sa.Column(
            "finding_id",
            sa.String(),
            nullable=False
        ),

        sa.Column(
            "event",
            sa.String(50),
            nullable=False
        ),

        sa.Column(
            "old_status",
            finding_status_enum,
            nullable=True
        ),

        sa.Column(
            "new_status",
            finding_status_enum,
            nullable=True
        ),

        sa.Column(
            "actor",
            sa.String(100),
            nullable=True
        ),

        sa.Column(
            "notes",
            sa.Text(),
            nullable=True
        ),

        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text(
                "now()"
            ),
            nullable=True
        ),

        sa.PrimaryKeyConstraint(
            "id"
        )
    )


    op.create_index(
        "idx_finding_events_finding_id",
        "finding_events",
        ["finding_id"]
    )


def downgrade() -> None:

    conn = op.get_bind()

    inspector = sa.inspect(conn)

    if "finding_events" in inspector.get_table_names():

        indexes = [
            idx["name"]
            for idx in inspector.get_indexes(
                "finding_events"
            )
        ]

        if "idx_finding_events_finding_id" in indexes:
            op.drop_index(
                "idx_finding_events_finding_id",
                table_name="finding_events"
            )

        op.drop_table(
            "finding_events"
        )