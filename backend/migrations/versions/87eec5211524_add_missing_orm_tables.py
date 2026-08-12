# backend/migrations/versions/87eec5211524_add_missing_orm_tables.py
# KEEP ONLY THE 4 CREATE TABLES + THEIR DOWNGRADES

"""add_missing_orm_tables

Revision ID: 87eec5211524
Revises: 0aef74f7d0dc
Create Date: 2026-08-08 09:04:14.468644
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '87eec5211524'
down_revision: Union[str, None] = '0aef74f7d0dc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # CREATE dashboard_view
    op.create_table('dashboard_view',
        sa.Column('case_id', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('fraud_score', sa.Float(), nullable=True),
        sa.Column('risk_score', sa.Float(), nullable=True),
        sa.Column('risk_level', sa.String(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('analysis_count', sa.Integer(), nullable=True),
        sa.Column('evidence_count', sa.Integer(), nullable=True),
        sa.Column('total_events', sa.Integer(), nullable=True),
        sa.Column('avg_confidence', sa.Float(), nullable=True),
        sa.Column('latest_fraud', sa.JSON(), nullable=True),
        sa.Column('latest_risk', sa.JSON(), nullable=True),
        sa.Column('latest_graph', sa.JSON(), nullable=True),
        sa.Column('latest_evidence', sa.JSON(), nullable=True),
        sa.Column('latest_procurement', sa.JSON(), nullable=True),
        sa.Column('last_updated', sa.DateTime(timezone=True), nullable=False),
        sa.Column('version', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('case_id')
    )
    
    # CREATE evidence
    op.create_table('evidence',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('case_id', sa.String(), nullable=False),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('file_hash', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=False),
        sa.Column('verified_at', sa.DateTime(), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('file_path', sa.String(), nullable=False),
        sa.Column('mime_type', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('verified_by', sa.String(), nullable=True),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('institution_id', sa.String(), nullable=False),
        sa.Column('created_by', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('trust_score', sa.Float(), nullable=True),
        sa.Column('file_type', sa.String(), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # CREATE processed_events
    op.create_table('processed_events',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('event_id', sa.String(length=255), nullable=False),
        sa.Column('projection_name', sa.String(length=100), nullable=False),
        sa.Column('aggregate_id', sa.String(length=255), nullable=True),
        sa.Column('event_sequence', sa.Integer(), nullable=True),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('event_id', 'projection_name', name='uq_processed_event')
    )
    
    # CREATE projection_checkpoints
    op.create_table('projection_checkpoints',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('projection_name', sa.String(length=100), nullable=False),
        sa.Column('last_sequence', sa.Integer(), nullable=False),
        sa.Column('total_processed', sa.Integer(), nullable=False),
        sa.Column('total_failed', sa.Integer(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_projection_checkpoints_projection_name'), 'projection_checkpoints', ['projection_name'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_projection_checkpoints_projection_name'), table_name='projection_checkpoints')
    op.drop_table('projection_checkpoints')
    op.drop_table('processed_events')
    op.drop_table('evidence')
    op.drop_table('dashboard_view')