"""create evidence files table

Revision ID: bbcaefb27b5f
Revises: 85a1e0f0e091
Create Date: 2026-08-08 19:33:06.781942

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'bbcaefb27b5f'
down_revision: Union[str, None] = '85a1e0f0e091'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "evidence_files",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "case_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "filename",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "sha256_hash",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "file_size",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "mime_type",
            sa.String(),
            nullable=True,
        ),
        sa.Column(
            "uploaded_by",
            sa.String(),
            nullable=True,
        ),
        sa.Column(
            "uploaded_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column(
            "metadata",
            postgresql.JSONB(),
            nullable=True,
        ),
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            server_default=sa.text("FALSE"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["case_id"],
            ["cases.id"],
            ondelete="CASCADE",
        ),
    )

    op.create_index(
        "idx_evidence_files_case_id",
        "evidence_files",
        ["case_id"],
    )

    op.create_index(
        "idx_evidence_files_uploaded_at",
        "evidence_files",
        ["uploaded_at"],
    )

    op.create_index(
        "idx_evidence_files_is_deleted",
        "evidence_files",
        ["is_deleted"],
    )


def downgrade() -> None:
    op.drop_index(
        "idx_evidence_files_is_deleted",
        table_name="evidence_files",
    )
    op.drop_index(
        "idx_evidence_files_uploaded_at",
        table_name="evidence_files",
    )
    op.drop_index(
        "idx_evidence_files_case_id",
        table_name="evidence_files",
    )
    op.drop_table("evidence_files")