"""create_risk_explanations_table

Revision ID: 89b0e5f23a1c
Revises: 77a3e5d30975
Create Date: 2026-08-08

Creates risk_explanations table for risk factor explanations.

CONTRACT:
- Table is SQL_REPOSITORY managed (no ORM model)
- Used by: services/provenance.py, routers/cases.py,
  create_snapshots.py
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "89b0e5f23a1c"
down_revision: Union[str, None] = "77a3e5d30975"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "risk_explanations",
        sa.Column("id", sa.String, primary_key=True, nullable=False),
        sa.Column("case_id", sa.String, nullable=False),
        sa.Column("factor", sa.String, nullable=False),
        sa.Column("score", sa.Numeric, nullable=False),
        sa.Column("weight", sa.Numeric, nullable=False),
        sa.Column("contribution", sa.Numeric, nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
    )

    op.create_index(
        "idx_risk_expl_case_id",
        "risk_explanations",
        ["case_id"],
    )

    op.create_index(
        "idx_risk_expl_contribution",
        "risk_explanations",
        ["contribution"],
    )


def downgrade() -> None:
    op.drop_index(
        "idx_risk_expl_contribution",
        table_name="risk_explanations",
    )

    op.drop_index(
        "idx_risk_expl_case_id",
        table_name="risk_explanations",
    )

    op.drop_table("risk_explanations")