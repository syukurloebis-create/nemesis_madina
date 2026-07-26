"""repair_pattern_detections_table

Revision ID: 3d94f136531d
Revises: 7703ce038868
Create Date: 2026-07-22 11:30:53.488763

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3d94f136531d'
down_revision: Union[str, None] = '7703ce038868'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create pattern_detections table if not exists."""
    op.execute("""
    CREATE TABLE IF NOT EXISTS pattern_detections (
        id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
        case_id uuid NOT NULL,
        pattern_type varchar(100) NOT NULL,
        severity varchar(20) NOT NULL,
        confidence_score double precision NOT NULL,
        is_validated boolean NOT NULL DEFAULT false,
        detected_at timestamp DEFAULT now(),
        created_at timestamp DEFAULT now(),
        updated_at timestamp DEFAULT now()
    )
    """)

    op.execute("""
    CREATE INDEX IF NOT EXISTS ix_pattern_detections_case_id
    ON pattern_detections(case_id)
    """)


def downgrade() -> None:
    """Drop pattern_detections table if exists."""
    op.execute("DROP INDEX IF EXISTS ix_pattern_detections_case_id")
    op.execute("DROP TABLE IF EXISTS pattern_detections")