"""merge finding action log branch

Revision ID: 721b0926d105
Revises: xxxx, 50990552f7ee
Create Date: 2026-06-28 05:47:00.723309

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "721b0926d105"
down_revision: Union[str, None] = "50990552f7ee"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass