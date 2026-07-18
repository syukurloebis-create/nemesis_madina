"""merge all intelligence heads

Revision ID: 08b8335dcf62
Revises: 04a7600b53fa, 7b64a52a6076, add_graph_metrics, add_graph_node_scores
Create Date: 2026-07-12 17:42:46.528320

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '08b8335dcf62'
down_revision: Union[str, None] = ('04a7600b53fa', '7b64a52a6076', 'add_graph_metrics', 'add_graph_node_scores')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
