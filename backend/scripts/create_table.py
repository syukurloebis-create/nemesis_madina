#!/usr/bin/env python3
import asyncio
import sys
sys.path.insert(0, '.')

from infrastructure.database import AsyncSessionLocal
from sqlalchemy import text

async def create_table():
    async with AsyncSessionLocal() as session:
        await session.execute(text("""
            CREATE TABLE IF NOT EXISTS rup_paket_detailed (
                id SERIAL PRIMARY KEY,
                kode_paket VARCHAR(50),
                kode_rup VARCHAR(50),
                tahun_anggaran INTEGER,
                nama_instansi VARCHAR(255),
                satuan_kerja VARCHAR(255),
                nama_penyedia VARCHAR(255),
                nama_paket TEXT,
                total_nilai NUMERIC(20,0),
                nilai_pdn NUMERIC(20,0),
                sumber_transaksi VARCHAR(100),
                sumber_dana VARCHAR(50),
                metode_pengadaan VARCHAR(100),
                jenis_pengadaan VARCHAR(100),
                status_paket VARCHAR(100),
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """))
        await session.commit()
        print("✅ Table rup_paket_detailed created successfully")

async def create_indexes():
    async with AsyncSessionLocal() as session:
        await session.execute(text("CREATE INDEX IF NOT EXISTS idx_rup_detailed_kode_paket ON rup_paket_detailed(kode_paket)"))
        await session.execute(text("CREATE INDEX IF NOT EXISTS idx_rup_detailed_penyedia ON rup_paket_detailed(nama_penyedia)"))
        await session.execute(text("CREATE INDEX IF NOT EXISTS idx_rup_detailed_instansi ON rup_paket_detailed(nama_instansi)"))
        await session.execute(text("CREATE INDEX IF NOT EXISTS idx_rup_detailed_tahun ON rup_paket_detailed(tahun_anggaran)"))
        await session.commit()
        print("✅ Indexes created successfully")

async def main():
    await create_table()
    await create_indexes()

if __name__ == "__main__":
    asyncio.run(main())