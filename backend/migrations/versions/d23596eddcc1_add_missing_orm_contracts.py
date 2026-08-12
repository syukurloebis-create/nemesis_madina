"""add_missing_orm_contracts

Revision ID: d23596eddcc1
Revises: 87eec5211524
Create Date: 2026-08-08 10:59:38.096886

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd23596eddcc1'
down_revision: Union[str, None] = '87eec5211524'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ============================================================
    # TABLE 1: chain_of_custody
    # ORM: backend/evidence/models.py:54-72
    # Contract: No FK, application-side timestamps
    # ============================================================
    op.create_table(
        'chain_of_custody',
        sa.Column('id', sa.Integer, autoincrement=True, nullable=False),
        sa.Column('evidence_id', sa.String, nullable=False),
        sa.Column('action', sa.String, nullable=False),
        sa.Column('user_id', sa.String, nullable=False),
        sa.Column('user_name', sa.String, nullable=False),
        sa.Column('institution_id', sa.String, nullable=False),
        sa.Column('ip_address', sa.String, nullable=True),
        sa.Column('user_agent', sa.String, nullable=True),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Performance index (verified by 50+ file usage querying by evidence_id)
    # NOTE: This is a performance index, NOT an ORM structural contract
    op.create_index('idx_coc_evidence_id', 'chain_of_custody', ['evidence_id'])

    # ============================================================
    # TABLE 2: fraud_detections
    # ORM: backend/intelligence/models.py:183-220
    # Contract: 
    #   - ORM-side UUID (NO server_default)
    #   - ORM-side updated_at (NO DB trigger/default)
    #   - TIMESTAMP WITHOUT TIME ZONE (matches ORM DateTime)
    # ============================================================
    op.create_table(
        'fraud_detections',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('case_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('detection_type', sa.String, nullable=False),
        sa.Column('severity', sa.String, nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('confidence', sa.Float, nullable=False),
        sa.Column('detected_at', sa.DateTime(), server_default=sa.text('NOW()')),
        sa.Column('reviewed_at', sa.DateTime(), nullable=True),
        sa.Column('reviewed_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('status', sa.String, nullable=False, server_default='PENDING'),
        sa.Column('findings', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        # NO onupdate — ORM handles this at runtime
        sa.ForeignKeyConstraint(['case_id'], ['cases.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Essential indexes from query patterns
    op.create_index('idx_fraud_case_id', 'fraud_detections', ['case_id'])
    op.create_index('idx_fraud_status', 'fraud_detections', ['status'])
    op.create_index('idx_fraud_detected_at', 'fraud_detections', ['detected_at'])

    # ============================================================
    # TABLE 3: outbox_messages
    # ORM: backend/infrastructure/models/outbox.py:18-43
    # Contract: 
    #   - ENUM: UPPERCASE (verified from SQLAlchemy behavior)
    #   - Unique constraint on event_id (creates unique index)
    #   - Composite indexes from __table_args__
    #   - Individual indexes from index=True
    #   - NO redundant non-unique index on event_id
    # ============================================================
    
    # Create ENUM with UPPERCASE values (matching ORM contract)
    # SQLAEnum(OutboxStatus) with no values_callable → persists .name (UPPERCASE)
    outbox_status_enum = postgresql.ENUM(
        'PENDING',
        'PROCESSING',
        'COMPLETED',
        'FAILED',
        'RETRY',
        name='outboxstatus',
        create_type=False,
    )
    outbox_status_enum.create(op.get_bind(), checkfirst=True)
    
    op.create_table(
        'outbox_messages',
        sa.Column('id', sa.Integer, autoincrement=True, nullable=False),
        sa.Column('event_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('aggregate_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('event_type', sa.String(255), nullable=False),
        sa.Column('payload', postgresql.JSONB, nullable=False),
        sa.Column(
            'status',
            outbox_status_enum,
            nullable=False,
            server_default='PENDING'  # UPPERCASE — verified contract
        ),
        sa.Column('retry_count', sa.Integer, nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.String, nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('event_id', name='uq_outbox_event_id')
        # Unique constraint creates a UNIQUE index — no separate non-unique index needed
    )
    
    # ============================================================
    # INDEXES: EXACTLY as defined in ORM __table_args__
    # ============================================================
    op.create_index(
        'idx_outbox_pending',
        'outbox_messages',
        ['status', 'created_at']
    )
    op.create_index(
        'idx_outbox_aggregate',
        'outbox_messages',
        ['aggregate_id', 'event_type']
    )
    
    # ============================================================
    # Individual column indexes: ONLY where ORM explicitly sets index=True
    # ============================================================
    # aggregate_id: index=True
    op.create_index('idx_outbox_aggregate_id', 'outbox_messages', ['aggregate_id'])
    # event_type: index=True
    op.create_index('idx_outbox_event_type', 'outbox_messages', ['event_type'])
    # event_id: index=True (BUT unique constraint already creates a unique index)
    # We do NOT create a separate non-unique index to avoid redundancy
    # The unique constraint 'uq_outbox_event_id' provides the index

def downgrade() -> None:
    # ============================================================
    # Reverse order: outbox_messages → fraud_detections → chain_of_custody
    # ============================================================
    
    # Drop outbox_messages and its indexes
    op.drop_index('idx_outbox_event_type', table_name='outbox_messages')
    op.drop_index('idx_outbox_aggregate_id', table_name='outbox_messages')
    op.drop_index('idx_outbox_aggregate', table_name='outbox_messages')
    op.drop_index('idx_outbox_pending', table_name='outbox_messages')
    op.drop_table('outbox_messages')
    
    # Drop ENUM
    outbox_status_enum = postgresql.ENUM(
        'PENDING',
        'PROCESSING',
        'COMPLETED',
        'FAILED',
        'RETRY',
        name='outboxstatus',
        create_type=False,
    )
    outbox_status_enum.drop(op.get_bind(), checkfirst=True)
    
    # Drop fraud_detections
    op.drop_index('idx_fraud_detected_at', table_name='fraud_detections')
    op.drop_index('idx_fraud_status', table_name='fraud_detections')
    op.drop_index('idx_fraud_case_id', table_name='fraud_detections')
    op.drop_table('fraud_detections')
    
    # Drop chain_of_custody
    op.drop_index('idx_coc_evidence_id', table_name='chain_of_custody')
    op.drop_table('chain_of_custody')