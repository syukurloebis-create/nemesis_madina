"""add_missing_case_columns

Revision ID: 983335c19d37
Revises: d23596eddcc1
Create Date: 2026-08-08 12:11:51.366765

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '983335c19d37'
down_revision: Union[str, None] = 'd23596eddcc1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Authoritative default tenant UUID from settings
# Source: backend/_deprecated_config_old.py:41-42
DEFAULT_TENANT_UUID = '11111111-1111-1111-1111-111111111111'


def upgrade() -> None:
    # ============================================================
    # ADD 15 MISSING CASE COLUMNS
    # ============================================================

    # priority - from CasePriority enum
    op.add_column(
        'cases',
        sa.Column('priority', sa.String, nullable=True)
    )

    # assigned_to - User UUID
    op.add_column(
        'cases',
        sa.Column(
            'assigned_to',
            postgresql.UUID(as_uuid=True),
            nullable=True
        )
    )

    # institution_id - Institution UUID
    op.add_column(
        'cases',
        sa.Column(
            'institution_id',
            postgresql.UUID(as_uuid=True),
            nullable=True
        )
    )

    # tenant_id - Multi-tenant isolation (NOT NULL with default)
    # Cases table is empty, so safe to add NOT NULL directly
    op.add_column(
        'cases',
        sa.Column(
            'tenant_id',
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text(f"'{DEFAULT_TENANT_UUID}'::uuid")
        )
    )

    # is_deleted - Soft delete flag
    op.add_column(
        'cases',
        sa.Column(
            'is_deleted',
            sa.Boolean,
            nullable=False,
            server_default='false'
        )
    )

    # deleted_at - Soft delete timestamp
    op.add_column(
        'cases',
        sa.Column('deleted_at', sa.DateTime, nullable=True)
    )

    # workflow_stage - Investigation workflow
    op.add_column(
        'cases',
        sa.Column('workflow_stage', sa.String(50), nullable=True)
    )

    # risk_score - Numeric risk score (0-100)
    op.add_column(
        'cases',
        sa.Column('risk_score', sa.Numeric(5, 2), nullable=True)
    )

    # risk_level - Risk classification
    op.add_column(
        'cases',
        sa.Column('risk_level', sa.String(20), nullable=True)
    )

    # review_notes - Review comments
    op.add_column(
        'cases',
        sa.Column('review_notes', sa.Text, nullable=True)
    )

    # review_by - Reviewer UUID
    op.add_column(
        'cases',
        sa.Column(
            'review_by',
            postgresql.UUID(as_uuid=True),
            nullable=True
        )
    )

    # review_at - Review timestamp
    op.add_column(
        'cases',
        sa.Column('review_at', sa.DateTime, nullable=True)
    )

    # assigned_at - Assignment timestamp
    op.add_column(
        'cases',
        sa.Column('assigned_at', sa.DateTime, nullable=True)
    )

    # investigation_started_at - Investigation start
    op.add_column(
        'cases',
        sa.Column('investigation_started_at', sa.DateTime, nullable=True)
    )

    # investigation_completed_at - Investigation completion
    op.add_column(
        'cases',
        sa.Column('investigation_completed_at', sa.DateTime, nullable=True)
    )


def downgrade() -> None:
    # ============================================================
    # REMOVE COLUMNS (reverse order)
    # ============================================================

    op.drop_column('cases', 'investigation_completed_at')
    op.drop_column('cases', 'investigation_started_at')
    op.drop_column('cases', 'assigned_at')
    op.drop_column('cases', 'review_at')
    op.drop_column('cases', 'review_by')
    op.drop_column('cases', 'review_notes')
    op.drop_column('cases', 'risk_level')
    op.drop_column('cases', 'risk_score')
    op.drop_column('cases', 'workflow_stage')
    op.drop_column('cases', 'deleted_at')
    op.drop_column('cases', 'is_deleted')
    op.drop_column('cases', 'tenant_id')
    op.drop_column('cases', 'institution_id')
    op.drop_column('cases', 'assigned_to')
    op.drop_column('cases', 'priority')