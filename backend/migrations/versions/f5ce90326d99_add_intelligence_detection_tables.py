"""add_intelligence_detection_tables

revision = "f5ce90326d99"
down_revision = "7e9dcf0e5a5d"
branch_labels = None
depends_on = None
Create Date: 2026-06-14 10:22:05.688971

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f5ce90326d99'
down_revision: Union[str, None] = '7e9dcf0e5a5d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# ============================================================================
# ENUM DEFINITIONS (with checkfirst=True for safety)
# ============================================================================

DetectionTypeEnum = postgresql.ENUM(
    "STATISTICAL",
    "GRAPH",
    "ML",
    "RULE",
    "TEMPORAL",
    name="detectiontype",
    create_type=False,
)

RiskLevelEnum = postgresql.ENUM(
    "CRITICAL",
    "HIGH",
    "MEDIUM",
    "LOW",
    "INFO",
    name="risklevel",
    create_type=False,
)

AlertSeverityEnum = postgresql.ENUM(
    "CRITICAL",
    "HIGH",
    "MEDIUM",
    "LOW",
    name="alertseverity",
    create_type=False,
)

AlertStatusEnum = postgresql.ENUM(
    "PENDING",
    "ACKNOWLEDGED",
    "RESOLVED",
    "DISMISSED",
    name="alertstatus",
    create_type=False,
)


def upgrade() -> None:
    # ========================================================================
    # CREATE ENUMS SAFELY (checkfirst=True prevents DuplicateObject)
    # ========================================================================
    bind = op.get_bind()
    
    DetectionTypeEnum.create(bind, checkfirst=True)
    RiskLevelEnum.create(bind, checkfirst=True)
    AlertSeverityEnum.create(bind, checkfirst=True)
    AlertStatusEnum.create(bind, checkfirst=True)

    # ========================================================================
    # CREATE TABLES
    # ========================================================================

    op.create_table('anomaly_detections',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('case_id', sa.UUID(), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=True),
        sa.Column("detection_type", DetectionTypeEnum, nullable=False),
        sa.Column('anomaly_type', sa.String(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('severity', sa.Float(), nullable=True),
        sa.Column('observed_value', sa.JSON(), nullable=True),
        sa.Column('expected_value', sa.JSON(), nullable=True),
        sa.Column('deviation', sa.Float(), nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('evidence', sa.JSON(), nullable=True),
        sa.Column('is_reviewed', sa.Boolean(), nullable=True),
        sa.Column('reviewed_by', sa.String(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('detected_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['case_id'], ['cases.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_anomaly_case_type', 'anomaly_detections', ['case_id', 'detection_type'], unique=False)
    op.create_index('idx_anomaly_severity', 'anomaly_detections', ['severity'], unique=False)
    op.create_index(op.f('ix_anomaly_detections_case_id'), 'anomaly_detections', ['case_id'], unique=False)

    op.create_table('intelligence_reports',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('case_id', sa.UUID(), nullable=False),
        sa.Column('report_type', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('content', sa.JSON(), nullable=False),
        sa.Column('generated_by', sa.String(), nullable=True),
        sa.Column('generated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('version', sa.Integer(), nullable=True),
        sa.Column('is_shared', sa.Boolean(), nullable=True),
        sa.Column('shared_with', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['case_id'], ['cases.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_report_case_type', 'intelligence_reports', ['case_id', 'report_type'], unique=False)
    op.create_index(op.f('ix_intelligence_reports_case_id'), 'intelligence_reports', ['case_id'], unique=False)

    op.create_table('risk_scores',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('case_id', sa.UUID(), nullable=False),
        sa.Column('entity_id', sa.String(), nullable=True),
        sa.Column('entity_type', sa.String(), nullable=True),
        sa.Column('overall_score', sa.Float(), nullable=False),
        sa.Column("risk_level", RiskLevelEnum, nullable=False),
        sa.Column('anomaly_score', sa.Float(), nullable=True),
        sa.Column('collusion_score', sa.Float(), nullable=True),
        sa.Column('financial_score', sa.Float(), nullable=True),
        sa.Column('temporal_score', sa.Float(), nullable=True),
        sa.Column('factors', sa.JSON(), nullable=True),
        sa.Column('recommendations', sa.JSON(), nullable=True),
        sa.Column('calculated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('calculated_by', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['case_id'], ['cases.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_risk_case_score', 'risk_scores', ['case_id', 'overall_score'], unique=False)
    op.create_index('idx_risk_entity', 'risk_scores', ['entity_id', 'entity_type'], unique=False)
    op.create_index(op.f('ix_risk_scores_case_id'), 'risk_scores', ['case_id'], unique=False)
    op.create_index(op.f('ix_risk_scores_entity_id'), 'risk_scores', ['entity_id'], unique=False)

    op.create_table('alerts',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('case_id', sa.UUID(), nullable=False),
        sa.Column('anomaly_id', sa.String(), nullable=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column("severity", AlertSeverityEnum, nullable=False),
        sa.Column("status", AlertStatusEnum, nullable=True),
        sa.Column('alert_type', sa.String(), nullable=False),
        sa.Column('triggered_by', sa.String(), nullable=True),
        sa.Column('assigned_to', sa.String(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolution_note', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['anomaly_id'], ['anomaly_detections.id'], ),
        sa.ForeignKeyConstraint(['case_id'], ['cases.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_alert_case_status', 'alerts', ['case_id', 'status'], unique=False)
    op.create_index('idx_alert_severity_status', 'alerts', ['severity', 'status'], unique=False)
    op.create_index(op.f('ix_alerts_case_id'), 'alerts', ['case_id'], unique=False)


def downgrade() -> None:
    bind = op.get_bind()

    # Drop tables
    op.drop_index(op.f('ix_alerts_case_id'), table_name='alerts')
    op.drop_index('idx_alert_severity_status', table_name='alerts')
    op.drop_index('idx_alert_case_status', table_name='alerts')
    op.drop_table('alerts')

    op.drop_index(op.f('ix_risk_scores_entity_id'), table_name='risk_scores')
    op.drop_index(op.f('ix_risk_scores_case_id'), table_name='risk_scores')
    op.drop_index('idx_risk_entity', table_name='risk_scores')
    op.drop_index('idx_risk_case_score', table_name='risk_scores')
    op.drop_table('risk_scores')

    op.drop_index(op.f('ix_intelligence_reports_case_id'), table_name='intelligence_reports')
    op.drop_index('idx_report_case_type', table_name='intelligence_reports')
    op.drop_table('intelligence_reports')

    op.drop_index(op.f('ix_anomaly_detections_case_id'), table_name='anomaly_detections')
    op.drop_index('idx_anomaly_severity', table_name='anomaly_detections')
    op.drop_index('idx_anomaly_case_type', table_name='anomaly_detections')
    op.drop_table('anomaly_detections')

    # Drop enums safely (checkfirst=True)
    AlertStatusEnum.drop(bind, checkfirst=True)
    AlertSeverityEnum.drop(bind, checkfirst=True)
    RiskLevelEnum.drop(bind, checkfirst=True)
    DetectionTypeEnum.drop(bind, checkfirst=True)