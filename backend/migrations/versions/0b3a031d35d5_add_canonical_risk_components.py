"""add canonical risk components

Revision ID: 0b3a031d35d5
Revises: add_business_key_source_id
Create Date: 2026-09-11 01:11:45.786460

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0b3a031d35d5'
down_revision: Union[str, None] = 'add_business_key_source_id'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # 1. Canonical component columns (risk-direction, 0-100)
    op.add_column('risk_scores', sa.Column('findings_risk', sa.Float(), nullable=True))
    op.add_column('risk_scores', sa.Column('graph_risk', sa.Float(), nullable=True))
    op.add_column('risk_scores', sa.Column('fraud_risk', sa.Float(), nullable=True))
    op.add_column('risk_scores', sa.Column('evidence_risk', sa.Float(), nullable=True))

    # 2. Full snapshot for audit/provenance
    op.add_column('risk_scores', sa.Column('components', sa.JSON(), nullable=True))
    op.add_column('risk_scores', sa.Column('weights', sa.JSON(), nullable=True))

    # 3. Unique constraint untuk cegah race condition
    # (sudah diverifikasi: 0 duplicates)
    op.create_unique_constraint(
        'uq_risk_scores_case_id',
        'risk_scores',
        ['case_id']
    )

    # 4. Semantic comments on legacy columns
    op.execute("""
        COMMENT ON COLUMN risk_scores.anomaly_score IS
        'DEPRECATED v3: gunakan findings_risk'
    """)
    op.execute("""
        COMMENT ON COLUMN risk_scores.collusion_score IS
        'DEPRECATED v3: gunakan graph_risk'
    """)
    op.execute("""
        COMMENT ON COLUMN risk_scores.financial_score IS
        'DEPRECATED v3: gunakan fraud_risk'
    """)
    op.execute("""
        COMMENT ON COLUMN risk_scores.temporal_score IS
        'DEPRECATED v3: temporal signal belum diimplementasikan'
    """)

    # 5. Backfill existing rows (jika ada)
    op.execute("""
        UPDATE risk_scores
        SET
            findings_risk = COALESCE(anomaly_score, 0),
            graph_risk = COALESCE(collusion_score, 0),
            fraud_risk = COALESCE(financial_score, 0),
            evidence_risk = 0,
            components = json_build_object(
                'findings_risk', COALESCE(anomaly_score, 0),
                'graph_risk', COALESCE(collusion_score, 0),
                'fraud_risk', COALESCE(financial_score, 0),
                'evidence_risk', 0
            ),
            weights = '{"findings": 0.30, "graph": 0.25, "fraud": 0.30, "evidence": 0.15}'::json
        WHERE findings_risk IS NULL
    """)


def downgrade():
    op.drop_constraint('uq_risk_scores_case_id', 'risk_scores', type_='unique')
    op.drop_column('risk_scores', 'weights')
    op.drop_column('risk_scores', 'components')
    op.drop_column('risk_scores', 'evidence_risk')
    op.drop_column('risk_scores', 'fraud_risk')
    op.drop_column('risk_scores', 'graph_risk')
    op.drop_column('risk_scores', 'findings_risk')