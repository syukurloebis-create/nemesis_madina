"""create investigation findings table

Revision ID: f1bb4961ae6a
Revises: 442f76504e98
Create Date: 2026-08-08 14:49:02.469620

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f1bb4961ae6a'
down_revision: Union[str, None] = '442f76504e98'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'investigation_findings',
        sa.Column('id', sa.String, primary_key=True, nullable=False),
        sa.Column('case_id', sa.String, nullable=False),
        sa.Column('finding_type', sa.String, nullable=False),
        sa.Column('severity', sa.String, nullable=False),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('evidence_ids', postgresql.JSON, nullable=True),
        sa.Column('status', sa.String, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
    )

    # Query pattern indexes
    op.create_index('idx_inv_findings_case_id', 'investigation_findings', ['case_id'])
    op.create_index('idx_inv_findings_status', 'investigation_findings', ['status'])
    op.create_index('idx_inv_findings_created_at', 'investigation_findings', ['created_at'])

def downgrade() -> None:
    op.drop_index('idx_inv_findings_created_at', table_name='investigation_findings')
    op.drop_index('idx_inv_findings_status', table_name='investigation_findings')
    op.drop_index('idx_inv_findings_case_id', table_name='investigation_findings')
    op.drop_table('investigation_findings')