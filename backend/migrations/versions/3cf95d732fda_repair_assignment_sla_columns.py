"""repair assignment sla columns (NO-OP - COMPATIBILITY MIGRATION)

Revision ID: 3cf95d732fda
Revises: aff37ab5b174
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "3cf95d732fda"
down_revision: Union[str, None] = "aff37ab5b174"
branch_labels: Union[str, Sequence[str], None] = None
depends_on = None

def upgrade() -> None:
    # NO-OP: All columns already added in aff37ab5b174
    pass

def downgrade() -> None:
    # NO-OP: Maintain history integrity
    pass
