"""add finding review decisions

Revision ID: 6d48d93222a5
Revises: 721b0926d105
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "6d48d93222a5"
down_revision: Union[str, None] = "721b0926d105"

branch_labels = None
depends_on = None


def upgrade():

    op.create_table(
        "finding_review_decisions",
        sa.Column(
            "id",
            postgresql.UUID(),
            server_default=sa.text("gen_random_uuid()"),
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
            "decision",
            sa.String(50),
            nullable=False,
        ),
        sa.Column(
            "rationale",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "confidence_score",
            sa.Float(),
            nullable=True,
        ),
        sa.Column(
            "decided_by",
            sa.String(100),
            nullable=True,
        ),
        sa.Column(
            "decided_at",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "idx_review_decision_finding",
        "finding_review_decisions",
        ["finding_id"],
    )


def downgrade():

    op.drop_index(
        "idx_review_decision_finding",
        table_name="finding_review_decisions",
    )

    op.drop_table("finding_review_decisions")
