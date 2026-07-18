-- backend/graph/infrastructure/migrations/versions/add_expression_indexes.py

"""Add expression unique indexes

Revision ID: add_expression_indexes
"""

from alembic import op
import sqlalchemy as sa


def upgrade():
    # Unique index: (case_id, business_key)
    op.execute("""
        CREATE UNIQUE INDEX uq_graph_entities_case_id_business_key
        ON graph_entities (case_id, (extra_data->>'business_key'))
        WHERE extra_data->>'business_key' IS NOT NULL
    """)
    
    # Unique index: (case_id, source_id, target_id, relationship_type)
    op.execute("""
        CREATE UNIQUE INDEX uq_graph_relationships_case_id_source_target_type
        ON graph_relationships (case_id, source_id, target_id, relationship_type)
    """)
    
    # Unique index: (case_id, version)
    op.execute("""
        CREATE UNIQUE INDEX uq_graph_metadata_case_id_version
        ON graph_metadata (case_id, version)
    """)


def downgrade():
    op.execute("DROP INDEX uq_graph_metadata_case_id_version")
    op.execute("DROP INDEX uq_graph_relationships_case_id_source_target_type")
    op.execute("DROP INDEX uq_graph_entities_case_id_business_key")