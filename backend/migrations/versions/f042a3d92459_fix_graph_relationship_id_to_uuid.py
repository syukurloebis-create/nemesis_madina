"""fix_graph_relationship_id_to_uuid

Revision ID: f042a3d92459
Revises: 8f55954028cb
Create Date: 2026-08-13 14:00:56.767010

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f042a3d92459'
down_revision: Union[str, None] = '8f55954028cb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():

    op.drop_constraint(
        "graph_relationships_pkey",
        "graph_relationships",
        type_="primary"
    )

    op.execute(
        "DROP SEQUENCE IF EXISTS graph_relationships_id_seq CASCADE"
    )

    op.alter_column(
        "graph_relationships",
        "id",
        existing_type=sa.Integer(),
        type_=sa.String(length=36),
        existing_nullable=False,
        server_default=None
    )

    op.create_primary_key(
        "graph_relationships_pkey",
        "graph_relationships",
        ["id"]
    )


def downgrade():
    pass
