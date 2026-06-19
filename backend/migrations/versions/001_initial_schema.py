"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2024-01-01

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create sequence for audit ordering
    op.execute("CREATE SEQUENCE IF NOT EXISTS global_audit_seq")
    
    # Events table
    op.create_table(
        'events',
        sa.Column('id', UUID(), nullable=False),
        sa.Column('aggregate_id', UUID(), nullable=False),
        sa.Column('aggregate_type', sa.String(63), nullable=False),
        sa.Column('event_type', sa.String(63), nullable=False),
        sa.Column('event_version', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('event_hash', sa.String(64), nullable=False),
        sa.Column('aggregate_hash', sa.String(64), nullable=True),
        sa.Column('previous_hash', sa.String(64), nullable=True),
        sa.Column('event_signature', sa.String(512), nullable=True),
        sa.Column('signing_key_id', UUID(), nullable=True),
        sa.Column('payload', JSONB(), nullable=True),
        sa.Column('metadata', JSONB(), nullable=True),
        sa.Column('commit_position', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('created_by', UUID(), nullable=True),
        sa.Column('tenant_id', UUID(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('commit_position')
    )
    
    # Snapshots table
    op.create_table(
        'snapshots',
        sa.Column('id', UUID(), nullable=False),
        sa.Column('aggregate_id', UUID(), nullable=False),
        sa.Column('aggregate_type', sa.String(63), nullable=False),
        sa.Column('snapshot_version', sa.Integer(), nullable=False),
        sa.Column('snapshot_data', JSONB(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('created_by', UUID(), nullable=True),
        sa.Column('tenant_id', UUID(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_events_aggregate', 'events', ['aggregate_id', 'created_at'])
    op.create_index('idx_events_commit', 'events', ['commit_position'])
    op.create_index('idx_events_tenant', 'events', ['tenant_id'])
    op.create_index('idx_events_type', 'events', ['event_type'])
    op.create_index('idx_snapshots_aggregate', 'snapshots', ['aggregate_id', 'snapshot_version'])
    op.create_index('idx_snapshots_tenant', 'snapshots', ['tenant_id'])

def downgrade() -> None:
    op.drop_table('snapshots')
    op.drop_table('events')
    op.execute("DROP SEQUENCE IF EXISTS global_audit_seq")