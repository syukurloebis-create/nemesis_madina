"""increase_kode_rup_length_to_100

Revision ID: increase_kode_rup_length
Revises: f042a3d92459
Create Date: 2026-08-15 10:12:12

This migration increases the length of kode_rup column from VARCHAR(50) to VARCHAR(100)
to accommodate multi-RUP composite values (e.g., record with 6 RUP codes).

Background:
- Baseline contains a record with 6 RUP codes: 41552975;41552976;41552977;41552979;41552980;41552981
- This value is 53 characters long
- Current VARCHAR(50) cannot store this value
- 7 multi-RUP records are preserved in baseline
- 2 malformed records (2604, 3392) are quarantined

This is a contract amendment to align database schema with source data contract.
No data mutation is performed. Database remains at 0 rows after this migration.
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'increase_kode_rup_length'
down_revision: Union[str, None] = 'f042a3d92459'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.alter_column(
        'rup_paket_detailed',
        'kode_rup',
        existing_type=sa.String(length=50),
        type_=sa.String(length=100),
        existing_nullable=True
    )

def downgrade() -> None:
    op.alter_column(
        'rup_paket_detailed',
        'kode_rup',
        existing_type=sa.String(length=100),
        type_=sa.String(length=50),
        existing_nullable=True
    )
