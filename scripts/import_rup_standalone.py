import pandas as pd
import psycopg2
import uuid
import os
from datetime import datetime

# Koneksi database
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="nemesis_db",
    user="nemesis",
    password="nemesis123"
)
cursor = conn.cursor()

# Path file Excel - cek di beberapa lokasi
possible_paths = [
    'data_rup_madina.xlsx',
    'scripts/data_rup_madina.xlsx',
    '../data_rup_madina.xlsx',
    os.path.join(os.path.dirname(__file__), 'data_rup_madina.xlsx')
]

file_path = None
for path in possible_paths:
    if os.path.exists(path):
        file_path = path
        break

if not file_path:
    print("❌ File data_rup_madina.xlsx tidak ditemukan!")
    print("📁 Pastikan file ada di direktori: ~/nemesis_madina/")
    exit(1)

print(f"📁 Reading file: {file_path}")

# Baca file Excel
df = pd.read_excel(file_path)

print(f"📊 Total rows found: {len(df)}")
print(f"📋 Columns: {df.columns.tolist()}")

count = 0
error_count = 0
skip_count = 0

for index, row in df.iterrows():
    try:
        # Mapping kolom dari file Excel
        paket_id = str(row.get('nomor_id', ''))
        nama_paket = str(row.get('nama_paket', ''))
        pagu = float(row.get('pagu', 0)) if pd.notna(row.get('pagu')) else 0
        jenis = str(row.get('jenis', ''))
        tahun = int(row.get('tahun', 2025)) if pd.notna(row.get('tahun')) else 2025
        instansi = str(row.get('instansi', ''))
        lokasi = str(row.get('lokasi', 'Mandailing Natal'))
        metode = str(row.get('metode', ''))
        bulan = str(row.get('bulan', ''))
        kategori = str(row.get('kategori', ''))
        
        # Skip jika data tidak lengkap
        if not paket_id or paket_id == 'nan' or paket_id == '':
            skip_count += 1
            continue
            
        if not nama_paket or nama_paket == 'nan' or nama_paket == '':
            skip_count += 1
            continue
        
        # Cek apakah sudah ada
        cursor.execute("SELECT COUNT(*) FROM rup_data WHERE paket_id = %s", (paket_id,))
        exists = cursor.fetchone()[0]
        
        if exists:
            # Update
            cursor.execute("""
                UPDATE rup_data SET
                    nama_paket = %s,
                    pagu = %s,
                    jenis_pengadaan = %s,
                    tahun = %s,
                    instansi = %s,
                    lokasi = %s,
                    metode = %s,
                    bulan = %s,
                    kategori = %s,
                    updated_at = NOW()
                WHERE paket_id = %s
            """, (nama_paket, pagu, jenis, tahun, instansi, lokasi, metode, bulan, kategori, paket_id))
        else:
            # Insert
            cursor.execute("""
                INSERT INTO rup_data (
                    id, paket_id, nama_paket, pagu, jenis_pengadaan, 
                    tahun, instansi, lokasi, status, sumber_data,
                    metode, bulan, kategori, created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s
                )
            """, (
                str(uuid.uuid4()), paket_id, nama_paket, pagu, jenis,
                tahun, instansi, lokasi, 'ACTIVE', 'LPSE',
                metode, bulan, kategori, datetime.now(), datetime.now()
            ))
        
        count += 1
        
        if count % 500 == 0:
            conn.commit()
            print(f"✅ Imported {count} records...")
            
    except Exception as e:
        print(f"❌ Error at row {index}: {e}")
        error_count += 1
        continue

conn.commit()
print(f"\n{'='*50}")
print(f"📊 IMPORT COMPLETE!")
print(f"✅ Success: {count} records")
print(f"⚠️ Skipped (invalid data): {skip_count} records")
print(f"❌ Errors: {error_count} records")
print(f"📁 Total in file: {len(df)} records")
print(f"{'='*50}")

# Tampilkan statistik
cursor.execute("""
    SELECT 
        COUNT(*) as total,
        SUM(pagu) as total_budget,
        COUNT(CASE WHEN tahun = 2025 THEN 1 END) as tahun_2025,
        COUNT(CASE WHEN tahun = 2026 THEN 1 END) as tahun_2026
    FROM rup_data
""")
row = cursor.fetchone()
print(f"\n📊 DATABASE STATISTICS:")
print(f"   Total Records: {row[0]}")
print(f"   Total Budget: Rp {row[1]:,.0f}" if row[1] else "   Total Budget: Rp 0")
print(f"   Year 2025: {row[2]} packages")
print(f"   Year 2026: {row[3]} packages")

cursor.close()
conn.close()
