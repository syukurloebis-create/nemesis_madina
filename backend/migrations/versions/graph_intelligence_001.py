"""Add graph intelligence tables

Revision ID: graph_intelligence_001
Revises:
Create Date: 2026-06-20
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

def upgrade():
    # 1. graph_node_scores
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
    
    # 2. graph_clusters
    op.create_table(
        'graph_clusters',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('entity_id', sa.String(36), nullable=False),
        sa.Column('cluster_id', sa.Integer, nullable=False),
        sa.Column('case_id', sa.String(36), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['entity_id'], ['graph_entities.id'])
    )
    
    # 3. fraud_evidence
    op.create_table(
        'fraud_evidence',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('case_id', sa.String(36), nullable=False),
        sa.Column('entity_id', sa.String(36), nullable=True),
        sa.Column('evidence_type', sa.String(100), nullable=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('score', sa.Float, nullable=True),
        sa.Column('confidence', sa.Float, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['entity_id'], ['graph_entities.id'])
    )

def downgrade():
    op.drop_table('fraud_evidence')
    op.drop_table('graph_clusters')
    op.drop_table('graph_node_scores')
