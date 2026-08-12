"""create canonical tenants table

Revision ID: 4c60c838bdd2
Revises: 911d8bbac9d1
Create Date: 2026-08-11 14:57:48.964786

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '4c60c838bdd2'
down_revision: Union[str, None] = '911d8bbac9d1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TENANT_ITJEN = "11111111-1111-1111-1111-111111111111"
TENANT_KPK = "22222222-2222-2222-2222-222222222222"
TENANT_KEJAGUNG = "33333333-3333-3333-3333-333333333333"
TENANT_BPKP = "44444444-4444-4444-4444-444444444444"


def upgrade() -> None:
    op.create_table(
        "tenants",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "name",
            sa.String(255),
            nullable=False,
        ),
        sa.Column(
            "code",
            sa.String(50),
            nullable=False,
        ),
        sa.Column(
            "is_active",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "code",
            name="tenants_code_key",
        ),
    )

    op.execute(
        sa.text(
            """
            INSERT INTO tenants
                (id, name, code)
            VALUES
                (:itjen_id, :itjen_name, :itjen_code),
                (:kpk_id, :kpk_name, :kpk_code),
                (:kejagung_id, :kejagung_name, :kejagung_code),
                (:bpkp_id, :bpkp_name, :bpkp_code)
            """
        ).bindparams(
            itjen_id=TENANT_ITJEN,
            itjen_name="Inspektorat Jenderal",
            itjen_code="ITJEN",
            kpk_id=TENANT_KPK,
            kpk_name="Komisi Pemberantasan Korupsi",
            kpk_code="KPK",
            kejagung_id=TENANT_KEJAGUNG,
            kejagung_name="Kejaksaan Agung",
            kejagung_code="KEJAGUNG",
            bpkp_id=TENANT_BPKP,
            bpkp_name="Badan Pengawasan Keuangan dan Pembangunan",
            bpkp_code="BPKP",
        )
    )


def downgrade() -> None:
    op.drop_table("tenants")