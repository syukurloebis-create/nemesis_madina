"""add version and latest analysis columns

Revision ID: xxxxxxxxxxxx
Revises: 08b8335dcf62
Create Date: 2026-07-12

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision = "xxxxxxxxxxxx"
down_revision = "08b8335dcf62"
branch_labels = None
depends_on = None


def upgrade():
    # 1. Add version column with server default
    op.add_column(
        'cases',
        sa.Column(
            'version',
            sa.Integer(),
            nullable=False,
            server_default='0',
        )
    )

    # 2. Add CHECK constraint for version >= 0
    op.create_check_constraint(
        'ck_cases_version_non_negative',
        'cases',
        'version >= 0'
    )

    # 3. Add latest_* JSONB columns
    op.add_column('cases', sa.Column('latest_fraud', JSONB, nullable=True))
    op.add_column('cases', sa.Column('latest_risk', JSONB, nullable=True))
    op.add_column('cases', sa.Column('latest_evidence', JSONB, nullable=True))
    op.add_column('cases', sa.Column('latest_graph', JSONB, nullable=True))
    op.add_column('cases', sa.Column('latest_procurement', JSONB, nullable=True))

    # 4. Add GIN indexes for frequently queried JSONB columns
    op.create_index('idx_cases_latest_risk', 'cases', ['latest_risk'], postgresql_using='gin')
    op.create_index('idx_cases_latest_fraud', 'cases', ['latest_fraud'], postgresql_using='gin')


def downgrade():
    op.drop_index('idx_cases_latest_fraud', table_name='cases')
    op.drop_index('idx_cases_latest_risk', table_name='cases')
    op.drop_column('cases', 'latest_procurement')
    op.drop_column('cases', 'latest_graph')
    op.drop_column('cases', 'latest_evidence')
    op.drop_column('cases', 'latest_risk')
    op.drop_column('cases', 'latest_fraud')
    op.drop_constraint('ck_cases_version_non_negative', 'cases', type_='check')
    op.drop_column('cases', 'version')