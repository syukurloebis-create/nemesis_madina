#!/usr/bin/env python3
"""
Import data RUP yang sudah dinormalisasi ke database NEMESIS
"""

import pandas as pd
import psycopg2
from sqlalchemy import create_engine, text
import uuid
from datetime import datetime

# Konfigurasi database
DATABASE_URL = "postgresql://nemesis:nemesis123@localhost:5432/nemesis_db"

# File input
INPUT_FILE = "RUP_NORMALIZED.xlsx"

def create_tables_if_not_exists(engine):
    """Buat tabel untuk data RUP jika belum ada"""
    
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS rup_paket (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        nama_paket TEXT NOT NULL,
        pagu NUMERIC(20,2),
        jenis VARCHAR(50),
        tahun INTEGER,
        bulan DATE,
        kategori VARCHAR(50),
        metode VARCHAR(50),
        lokasi VARCHAR(100),
        instansi VARCHAR(100),
        nomor_id VARCHAR(50),
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
    );
    
    CREATE INDEX IF NOT EXISTS idx_rup_tahun ON rup_paket(tahun);
    CREATE INDEX IF NOT EXISTS idx_rup_instansi ON rup_paket(instansi);
    CREATE INDEX IF NOT EXISTS idx_rup_jenis ON rup_paket(jenis);
    CREATE INDEX IF NOT EXISTS idx_rup_metode ON rup_paket(metode);
    CREATE INDEX IF NOT EXISTS idx_rup_nomor ON rup_paket(nomor_id);
    """
    
    with engine.connect() as conn:
        conn.execute(text(create_table_sql))
        conn.commit()
    
    print("✅ Tabel rup_paket siap")

def import_data(engine, tahun):
    """Import data dari Excel ke database"""
    
    sheet_name = f'{tahun}_NORMALIZED'
    
    try:
        df = pd.read_excel(INPUT_FILE, sheet_name=sheet_name)
        print(f"📂 Membaca {len(df)} paket tahun {tahun}")
        
        # Konversi bulan ke date
        df['bulan_date'] = pd.to_datetime(df['bulan_normalized'], errors='coerce')
        
        # Pilih dan rename kolom
        df_import = df[['nama_paket', 'pagu_numeric', 'jenis_normalized', 'tahun', 
                        'bulan_date', 'kategori_normalized', 'metode_normalized', 
                        'lokasi', 'instansi_normalized', 'nomor_id']].copy()
        
        df_import.columns = ['nama_paket', 'pagu', 'jenis', 'tahun', 
                             'bulan', 'kategori', 'metode', 'lokasi', 'instansi', 'nomor_id']
        
        # Import ke database
        df_import.to_sql('rup_paket', engine, if_exists='append', index=False)
        
        print(f"   ✅ Import {len(df_import)} paket tahun {tahun} selesai")
        
    except Exception as e:
        print(f"   ❌ Error import tahun {tahun}: {e}")

def main():
    print("=" * 70)
    print("IMPORT DATA RUP KE NEMESIS")
    print("=" * 70)
    
    # Buat koneksi
    engine = create_engine(DATABASE_URL)
    
    # Cek koneksi
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Koneksi database berhasil")
    except Exception as e:
        print(f"❌ Koneksi database gagal: {e}")
        return
    
    # Buat tabel
    create_tables_if_not_exists(engine)
    
    # Import data
    print("\n📥 Memulai import data...")
    import_data(engine, 2025)
    import_data(engine, 2026)
    
    # Verifikasi
    print("\n📊 Verifikasi data di database:")
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT 
                tahun,
                COUNT(*) as total_paket,
                SUM(pagu) as total_pagu
            FROM rup_paket
            GROUP BY tahun
            ORDER BY tahun
        """))
        
        for row in result:
            print(f"   Tahun {row[0]}: {row[1]} paket, Rp {row[2]:,.0f}")
    
    print("\n" + "=" * 70)
    print("✅ IMPORT SELESAI!")
    print("=" * 70)

if __name__ == "__main__":
    main()
