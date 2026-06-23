"""Add graph_node_scores table

Revision ID: add_graph_node_scores
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'graph_node_scores',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('entity_id', sa.String(36), nullable=False),
        sa.Column('pagerank', sa.Float, nullable=True),
        sa.Column('degree', sa.Integer, nullable=True),
        sa.Column('weighted_degree', sa.Float, nullable=True),
        sa.Column('calculated_at', sa.TIMESTAMP, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['entity_id'], ['graph_entities.id']),
        sa.UniqueConstraint('entity_id', name='uq_entity_score')
    )

def downgrade():
    op.drop_table('graph_node_scores')
