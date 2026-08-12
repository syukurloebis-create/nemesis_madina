"""create_infrastructure_tables

Revision ID: 911d8bbac9d1
Revises: 0ed28900d4fa
Create Date: 2026-08-09 15:41:44.898297

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '911d8bbac9d1'
down_revision: Union[str, None] = '0ed28900d4fa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "investigation_recommendations",
        sa.Column("id", sa.String(), primary_key=True, nullable=False),
        sa.Column("recommendation_type", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("priority", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column(
            "due_date",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column("finding_id", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
    )

    op.create_index(
        "idx_inv_recomm_finding_id",
        "investigation_recommendations",
        ["finding_id"],
    )

    op.create_index(
        "idx_inv_recomm_created_at",
        "investigation_recommendations",
        ["created_at"],
    )

    op.create_table(
        "model_metrics",
        sa.Column("id", sa.String(), primary_key=True, nullable=False),
        sa.Column("model_name", sa.String(), nullable=False),
        sa.Column("version", sa.String(), nullable=False),
        sa.Column("accuracy", sa.Float(), nullable=False),
        sa.Column("model_type", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
    )

    op.create_index(
        "idx_model_metrics_model_name",
        "model_metrics",
        ["model_name"],
    )

    op.create_index(
        "idx_model_metrics_created_at",
        "model_metrics",
        ["created_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "idx_model_metrics_created_at",
        table_name="model_metrics",
    )
    op.drop_index(
        "idx_model_metrics_model_name",
        table_name="model_metrics",
    )
    op.drop_table("model_metrics")

    op.drop_index(
        "idx_inv_recomm_created_at",
        table_name="investigation_recommendations",
    )
    op.drop_index(
        "idx_inv_recomm_finding_id",
        table_name="investigation_recommendations",
    )
    op.drop_table("investigation_recommendations")