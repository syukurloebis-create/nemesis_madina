"""merge heads

Revision ID: 8fc3f98fb015
Revises: 001, 7470758e26b2
Create Date: 2026-06-13 23:05:40.446493

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8fc3f98fb015'
down_revision: Union[str, None] = ('001', '7470758e26b2')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
