# scripts/import_rup_data.py
import asyncio
import pandas as pd
import uuid
from sqlalchemy import text
from backend.database import get_db

async def import_rup_data():
    """Import data RUP dari file Excel"""
    
    # Baca file Excel
    df = pd.read_excel('data_rup_madina.xlsx')
    
    print(f"📊 Total rows found: {len(df)}")
    print(f"📋 Columns: {df.columns.tolist()}")
    
    async for db in get_db():
        count = 0
        error_count = 0
        
        for index, row in df.iterrows():
            try:
                # Mapping kolom dari file Excel ke database
                paket_id = str(row.get('nomor_id', ''))
                nama_paket = str(row.get('nama_paket', ''))
                pagu = float(row.get('pagu', 0))
                jenis = str(row.get('jenis', ''))
                tahun = int(row.get('tahun', 2025))
                instansi = str(row.get('instansi', ''))
                lokasi = str(row.get('lokasi', 'Mandailing Natal'))
                metode = str(row.get('metode', ''))
                bulan = str(row.get('bulan', ''))
                kategori = str(row.get('kategori', ''))
                
                # Skip jika data tidak lengkap
                if not paket_id or paket_id == 'nan':
                    print(f"⚠️ Row {index}: Missing paket_id, skipping...")
                    error_count += 1
                    continue
                    
                if not nama_paket or nama_paket == 'nan':
                    print(f"⚠️ Row {index}: Missing nama_paket, skipping...")
                    error_count += 1
                    continue
                
                # Simpan ke database
                query = text("""
                    INSERT INTO rup_data (
                        id, paket_id, nama_paket, pagu, jenis_pengadaan, 
                        tahun, instansi, lokasi, status, sumber_data,
                        metode, bulan, kategori
                    ) VALUES (
                        :id, :paket_id, :nama_paket, :pagu, :jenis_pengadaan,
                        :tahun, :instansi, :lokasi, :status, :sumber_data,
                        :metode, :bulan, :kategori
                    ) ON CONFLICT (paket_id) DO UPDATE SET
                        nama_paket = EXCLUDED.nama_paket,
                        pagu = EXCLUDED.pagu,
                        updated_at = NOW()
                """)
                
                await db.execute(query, {
                    "id": str(uuid.uuid4()),
                    "paket_id": paket_id,
                    "nama_paket": nama_paket,
                    "pagu": pagu,
                    "jenis_pengadaan": jenis,
                    "tahun": tahun,
                    "instansi": instansi,
                    "lokasi": lokasi,
                    "status": "ACTIVE",
                    "sumber_data": "LPSE",
                    "metode": metode,
                    "bulan": bulan,
                    "kategori": kategori
                })
                count += 1
                
                if count % 500 == 0:
                    await db.commit()
                    print(f"✅ Imported {count} records...")
                    
            except Exception as e:
                print(f"❌ Error at row {index}: {e}")
                error_count += 1
                continue
        
        await db.commit()
        print(f"\n{'='*50}")
        print(f"📊 IMPORT COMPLETE!")
        print(f"✅ Success: {count} records")
        print(f"❌ Errors: {error_count} records")
        print(f"📁 Total: {len(df)} records")
        print(f"{'='*50}")

if __name__ == "__main__":
    asyncio.run(import_rup_data())