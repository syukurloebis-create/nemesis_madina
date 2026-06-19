"""Create rup_paket_detailed table as source of truth

Revision ID: 003
Revises: 002
Create Date: 2026-06-14
"""

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'rup_paket_detailed',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('kode_paket', sa.String(50), nullable=True),
        sa.Column('kode_rup', sa.String(50), nullable=True),
        sa.Column('tahun_anggaran', sa.Integer, nullable=True),
        sa.Column('nama_instansi', sa.String(255), nullable=True),
        sa.Column('satuan_kerja', sa.String(255), nullable=True),
        sa.Column('nama_penyedia', sa.String(255), nullable=True),
        sa.Column('nama_paket', sa.Text, nullable=True),
        sa.Column('total_nilai', sa.Numeric(20, 0), nullable=True),
        sa.Column('nilai_pdn', sa.Numeric(20, 0), nullable=True),
        sa.Column('sumber_transaksi', sa.String(100), nullable=True),
        sa.Column('sumber_dana', sa.String(50), nullable=True),
        sa.Column('metode_pengadaan', sa.String(100), nullable=True),
        sa.Column('jenis_pengadaan', sa.String(100), nullable=True),
        sa.Column('status_paket', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    
    # Create indexes
    op.create_index('idx_rup_detailed_kode_paket', 'rup_paket_detailed', ['kode_paket'])
    op.create_index('idx_rup_detailed_penyedia', 'rup_paket_detailed', ['nama_penyedia'])
    op.create_index('idx_rup_detailed_instansi', 'rup_paket_detailed', ['nama_instansi'])
    op.create_index('idx_rup_detailed_tahun', 'rup_paket_detailed', ['tahun_anggaran'])
    op.create_index('idx_rup_detailed_penyedia_tahun', 'rup_paket_detailed', ['nama_penyedia', 'tahun_anggaran'])


def downgrade():
    op.drop_index('idx_rup_detailed_penyedia_tahun')
    op.drop_index('idx_rup_detailed_tahun')
    op.drop_index('idx_rup_detailed_instansi')
    op.drop_index('idx_rup_detailed_penyedia')
    op.drop_index('idx_rup_detailed_kode_paket')
    op.drop_table('rup_paket_detailed')