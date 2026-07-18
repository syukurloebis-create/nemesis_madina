"""add finding fingerprint unique constraint

Revision ID: 4cc8a0a5030b
Revises: dfea47b1013e
Create Date: 2026-06-27 08:11:42.195986

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "4cc8a0a5030b"
down_revision: Union[str, None] = "7e9dcf0e5a5d"

branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:

    # Add fingerprint column
    op.add_column(
        "findings",
        sa.Column(
            "fingerprint",
            sa.String(length=64),
            nullable=True
        )
    )


    # Index for lookup performance
    op.create_index(
        "idx_findings_fingerprint",
        "findings",
        ["fingerprint"]
    )


    # Idempotency constraint
    op.create_unique_constraint(
        "uq_findings_case_type_method_fp",
        "findings",
        [
            "case_id",
            "finding_type",
            "detection_method",
            "fingerprint"
        ]
    )



def downgrade() -> None:

    op.drop_constraint(
        "uq_findings_case_type_method_fp",
        "findings",
        type_="unique"
    )


    op.drop_index(
        "idx_findings_fingerprint",
        table_name="findings"
    )


    op.drop_column(
        "findings",
        "fingerprint"
    )