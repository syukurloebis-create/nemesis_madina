"""add_business_key_source_id_to_graph_entities

Revision ID: add_business_key_source_id
Revises: increase_kode_rup_length
Create Date: 2026-08-15

This migration adds business_key and source_id columns to graph_entities:

- business_key: VARCHAR(255) NOT NULL
  - Part of business identity with entity_type
  - UNIQUE(entity_type, business_key) constraint

- source_id: INTEGER NULLABLE
  - Provenance reference to rup_paket_detailed.id
  - NO FOREIGN KEY (decoupled lifecycle)
  - Indexed for query performance

No data mutation is performed. graph_entities is currently empty (0 rows).

This migration is reversible via downgrade().

Contract reference: R16.3.1 - Schema Design Contract
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'add_business_key_source_id'
down_revision: Union[str, None] = 'increase_kode_rup_length'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add business_key column
    op.add_column(
        'graph_entities',
        sa.Column('business_key', sa.String(255), nullable=False)
    )

    # Add source_id column (provenance only, NO FK)
    op.add_column(
        'graph_entities',
        sa.Column('source_id', sa.Integer, nullable=True)
    )

    # Add unique constraint on (entity_type, business_key)
    op.create_unique_constraint(
        'uq_graph_entities_entity_type_business_key',
        'graph_entities',
        ['entity_type', 'business_key']
    )

    # Add indexes
    op.create_index(
        'idx_graph_entities_business_key',
        'graph_entities',
        ['business_key']
    )
    op.create_index(
        'idx_graph_entities_source_id',
        'graph_entities',
        ['source_id']
    )


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_graph_entities_source_id', table_name='graph_entities')
    op.drop_index('idx_graph_entities_business_key', table_name='graph_entities')

    # Drop unique constraint
    op.drop_constraint(
        'uq_graph_entities_entity_type_business_key',
        'graph_entities',
        type_='unique'
    )

    # Drop columns
    op.drop_column('graph_entities', 'source_id')
    op.drop_column('graph_entities', 'business_key')
