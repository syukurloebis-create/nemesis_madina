"""create custody chain and access log tables

Revision ID: 85a1e0f0e091
Revises: 89b0e5f23a1c
Create Date: 2026-08-08 15:57:00.284019

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '85a1e0f0e091'
down_revision: Union[str, None] = '89b0e5f23a1c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ============================================================
    # TABLE 1: custody_chain (12 columns)
    # ============================================================
    op.create_table(
        'custody_chain',
        sa.Column('id', sa.String, primary_key=True, nullable=False),
        sa.Column('evidence_id', sa.String, nullable=False),
        sa.Column('from_custodian', sa.String, nullable=False),
        sa.Column('to_custodian', sa.String, nullable=False),
        sa.Column('reason', sa.String, nullable=False),
        sa.Column('transferred_by', sa.String, nullable=False),
        sa.Column('transferred_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('status', sa.String, nullable=False),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('tenant_id', sa.String, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
    )

    # Indexes for custody_chain
    op.create_index('idx_custody_chain_evidence_id', 'custody_chain', ['evidence_id'])
    op.create_index('idx_custody_chain_status', 'custody_chain', ['status'])
    op.create_index('idx_custody_chain_transferred_at', 'custody_chain', ['transferred_at'])
    op.create_index('idx_custody_chain_tenant_id', 'custody_chain', ['tenant_id'])

    # Partial unique index for active custody invariant (TENANT-AWARE)
    # Ensures: only one active custody record per tenant per evidence
    op.execute("""
        CREATE UNIQUE INDEX uq_custody_chain_active_tenant_evidence
        ON custody_chain (tenant_id, evidence_id)
        WHERE status = 'active'
    """)

    # ============================================================
    # TABLE 2: access_log (10 columns)
    # ============================================================
    op.create_table(
        'access_log',
        sa.Column('id', sa.String, primary_key=True, nullable=False),
        sa.Column('evidence_id', sa.String, nullable=False),
        sa.Column('accessed_by', sa.String, nullable=False),
        sa.Column('access_type', sa.String, nullable=False),
        sa.Column('reason', sa.Text, nullable=True),
        sa.Column('duration', sa.Integer, nullable=True),
        sa.Column('accessed_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('status', sa.String, nullable=False),
        sa.Column('tenant_id', sa.String, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
    )

    # Indexes for access_log
    op.create_index('idx_access_log_evidence_id', 'access_log', ['evidence_id'])
    op.create_index('idx_access_log_accessed_at', 'access_log', ['accessed_at'])
    op.create_index('idx_access_log_status', 'access_log', ['status'])
    op.create_index('idx_access_log_tenant_id', 'access_log', ['tenant_id'])

    # Composite index for query pattern: WHERE evidence_id = ? ORDER BY accessed_at DESC
    op.execute("""
        CREATE INDEX idx_access_log_evidence_accessed
        ON access_log (evidence_id, accessed_at DESC)
    """)

def downgrade() -> None:
    # ============================================================
    # Drop access_log
    # ============================================================
    op.execute("DROP INDEX IF EXISTS idx_access_log_evidence_accessed")
    op.drop_index('idx_access_log_tenant_id', table_name='access_log')
    op.drop_index('idx_access_log_status', table_name='access_log')
    op.drop_index('idx_access_log_accessed_at', table_name='access_log')
    op.drop_index('idx_access_log_evidence_id', table_name='access_log')
    op.drop_table('access_log')

    # ============================================================
    # Drop custody_chain
    # ============================================================
    op.execute("DROP INDEX IF EXISTS uq_custody_chain_active_tenant_evidence")
    op.drop_index('idx_custody_chain_tenant_id', table_name='custody_chain')
    op.drop_index('idx_custody_chain_transferred_at', table_name='custody_chain')
    op.drop_index('idx_custody_chain_status', table_name='custody_chain')
    op.drop_index('idx_custody_chain_evidence_id', table_name='custody_chain')
    op.drop_table('custody_chain')