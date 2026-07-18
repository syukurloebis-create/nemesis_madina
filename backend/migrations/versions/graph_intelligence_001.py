"""
Graph Intelligence bootstrap tables
✅ Core graph tables needed for intelligence engine
✅ Created before graph entity metrics
"""

from alembic import op
import sqlalchemy as sa

# ============================================================================
# ALEMBIC METADATA
# ============================================================================

revision = "graph_intelligence_001"
down_revision = "7e9dcf0e5a5d"  # Parent: add_intelligence_graph_schema
branch_labels = None
depends_on = None

# ============================================================================
# MIGRATION
# ============================================================================

def upgrade():
    """Create graph_intelligence core tables."""
    
    # 1. graph_node_scores
    op.execute("""
    CREATE TABLE IF NOT EXISTS graph_node_scores (
        id SERIAL PRIMARY KEY,
        entity_id VARCHAR(36) NOT NULL,
        pagerank FLOAT,
        degree INTEGER,
        weighted_degree FLOAT,
        calculated_at TIMESTAMP DEFAULT now(),
        CONSTRAINT uq_entity_score UNIQUE(entity_id)
    )
    """)

    # 2. graph_clusters
    op.execute("""
    CREATE TABLE IF NOT EXISTS graph_clusters (
        id SERIAL PRIMARY KEY,
        entity_id VARCHAR(36) NOT NULL,
        cluster_id INTEGER NOT NULL,
        case_id VARCHAR(36),
        created_at TIMESTAMP DEFAULT now()
    )
    """)

    # 3. fraud_evidence
    op.execute("""
    CREATE TABLE IF NOT EXISTS fraud_evidence (
        id SERIAL PRIMARY KEY,
        case_id VARCHAR(36) NOT NULL,
        entity_id VARCHAR(36),
        evidence_type VARCHAR(100),
        description TEXT,
        score FLOAT,
        confidence FLOAT,
        created_at TIMESTAMP DEFAULT now()
    )
    """)


def downgrade():
    """Drop graph_intelligence core tables."""
    op.drop_table("fraud_evidence")
    op.drop_table("graph_clusters")
    op.drop_table("graph_node_scores")