"""create_investigation_timeline_table

Revision ID: 77a3e5d30975
Revises: f1bb4961ae6a
Create Date: 2026-08-08 14:54:56.305023

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '77a3e5d30975'
down_revision: Union[str, None] = 'f1bb4961ae6a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'investigation_timeline',
        sa.Column('id', sa.Integer, autoincrement=True, primary_key=True, nullable=False),
        sa.Column('case_id', sa.String, nullable=False),
        sa.Column('stage', sa.String, nullable=False),
        sa.Column('from_stage', sa.String, nullable=True),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
    )

    op.create_index('idx_inv_timeline_case_id', 'investigation_timeline', ['case_id'])
    op.create_index('idx_inv_timeline_created_at', 'investigation_timeline', ['created_at'])

def downgrade() -> None:
    op.drop_index('idx_inv_timeline_created_at', table_name='investigation_timeline')
    op.drop_index('idx_inv_timeline_case_id', table_name='investigation_timeline')
    op.drop_table('investigation_timeline')