-- backend/graph/infrastructure/migrations/versions/add_graph_constraints.py

"""Add graph constraints

Revision ID: add_graph_constraints
"""

from alembic import op
import sqlalchemy as sa


def upgrade():
    # Unique constraint: (case_id, business_key)
    op.create_unique_constraint(
        "uq_graph_entities_case_id_business_key",
        "graph_entities",
        ["case_id", sa.text("extra_data->>'business_key'")],
    )
    
    # Unique constraint: (case_id, source_id, target_id, relationship_type)
    op.create_unique_constraint(
        "uq_graph_relationships_case_id_source_target_type",
        "graph_relationships",
        ["case_id", "source_id", "target_id", "relationship_type"],
    )
    
    # Unique constraint: (case_id, version)
    op.create_unique_constraint(
        "uq_graph_metadata_case_id_version",
        "graph_metadata",
        ["case_id", "version"],
    )


def downgrade():
    op.drop_constraint("uq_graph_metadata_case_id_version", "graph_metadata")
    op.drop_constraint("uq_graph_relationships_case_id_source_target_type", "graph_relationships")
    op.drop_constraint("uq_graph_entities_case_id_business_key", "graph_entities")