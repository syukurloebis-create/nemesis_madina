"""create_pattern_detections_table

Revision ID: 7703ce038868
Revises: xxxxxxxxxxxx
Create Date: 2026-07-22 10:15:09.153643

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = '7703ce038868'
down_revision: Union[str, None] = 'xxxxxxxxxxxx'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create pattern_detections table."""
    op.create_table(
        'pattern_detections',
        sa.Column('id', UUID, primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('case_id', UUID, nullable=False, index=True),
        sa.Column('pattern_type', sa.String(100), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False),
        sa.Column('confidence_score', sa.Float, nullable=False),
        sa.Column('is_validated', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('detected_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )


def downgrade() -> None:
    """Drop pattern_detections table."""
    op.drop_table('pattern_detections')