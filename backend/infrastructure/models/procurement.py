# backend/infrastructure/models/procurement.py

"""
NEMESIS Madina - Procurement ORM Models
✅ Derived from manual_003_create_rup_paket_detailed.py
✅ Uses central Base from database.py
✅ Includes all indexes from migration
"""

from sqlalchemy import Column, Integer, String, Numeric, Text, DateTime, Index
from sqlalchemy.sql import func

from backend.database import Base


class RupPaketDetailed(Base):
    """
    ORM model for rup_paket_detailed table.
    
    ✅ 100% matches migration schema
    ✅ Uses central Base from database.py
    """

    __tablename__ = "rup_paket_detailed"

    __table_args__ = (
        Index("idx_rup_detailed_kode_paket", "kode_paket"),
        Index("idx_rup_detailed_penyedia", "nama_penyedia"),
        Index("idx_rup_detailed_instansi", "nama_instansi"),
        Index("idx_rup_detailed_tahun", "tahun_anggaran"),
        Index(
            "idx_rup_detailed_penyedia_tahun",
            "nama_penyedia",
            "tahun_anggaran",
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    kode_paket = Column(String(50), nullable=True)
    kode_rup = Column(String(50), nullable=True)
    tahun_anggaran = Column(Integer, nullable=True)
    nama_instansi = Column(String(255), nullable=True)
    satuan_kerja = Column(String(255), nullable=True)
    nama_penyedia = Column(String(255), nullable=True)
    nama_paket = Column(Text, nullable=True)
    total_nilai = Column(Numeric(20, 0), nullable=True)
    nilai_pdn = Column(Numeric(20, 0), nullable=True)
    sumber_transaksi = Column(String(100), nullable=True)
    sumber_dana = Column(String(50), nullable=True)
    metode_pengadaan = Column(String(100), nullable=True)
    jenis_pengadaan = Column(String(100), nullable=True)
    status_paket = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())