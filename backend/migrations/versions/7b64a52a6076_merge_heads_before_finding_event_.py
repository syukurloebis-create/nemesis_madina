"""merge heads before finding event metadata

Revision ID: 7b64a52a6076
Revises: 5145313e9e12, 6d48d93222a5
Create Date: 2026-06-28 07:36:27.553685

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "7b64a52a6076"
down_revision: Union[str, None] = ("5145313e9e12", "6d48d93222a5")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass