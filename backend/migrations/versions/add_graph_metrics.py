"""Add graph entity metrics table

Revision ID: add_graph_metrics
Revises:
Create Date: 2026-06-20
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'graph_entity_metrics',
        sa.Column('entity_id', sa.String(36), primary_key=True),
        sa.Column('degree_score', sa.Float, nullable=True),
        sa.Column('weighted_degree', sa.Float, nullable=True),
        sa.Column('pagerank_score', sa.Float, nullable=True),
        sa.Column('betweenness_score', sa.Float, nullable=True),
        sa.Column('risk_score', sa.Float, nullable=True),
        sa.Column('calculated_at', sa.TIMESTAMP, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['entity_id'], ['graph_entities.id'])
    )

def downgrade():
    op.drop_table('graph_entity_metrics')
