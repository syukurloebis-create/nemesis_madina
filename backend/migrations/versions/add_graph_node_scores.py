"""
Compatibility migration.

graph_node_scores was already created
by graph_intelligence_001.

This migration intentionally does nothing.
"""

from alembic import op


revision = "add_graph_node_scores"
down_revision = "graph_intelligence_001"
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
