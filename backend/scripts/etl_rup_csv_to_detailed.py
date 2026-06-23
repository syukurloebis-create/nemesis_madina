#!/usr/bin/env python3
"""
ETL: CSV RUP to rup_paket_detailed (Source of Truth)
"""

import asyncio
import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, '/app')

from infrastructure.database import AsyncSessionLocal
from sqlalchemy import text


def parse_rup_csv(file_path: str):
    """Parse RUP CSV with proper CSV handling"""
    
    data = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
        
        header_idx = None
        for i, line in enumerate(lines):
            if line and 'Nama Instansi' in line and 'Kode Paket' in line:
                header_idx = i
                break
        
        if header_idx is None:
            print("❌ Header not found")
            return []
        
        reader = csv.DictReader(lines[header_idx:], delimiter=',', quotechar='"')
        
        for row in reader:
            clean_row = {}
            for k, v in row.items():
                if k is None:
                    continue
                clean_key = str(k).strip().replace('\ufeff', '').replace(';;;;;', '').replace(';;;;', '')
                clean_value = v.strip() if v else None
                if clean_value:
                    clean_value = re.sub(r';+$', '', clean_value)
                    if clean_value.startswith('"') and clean_value.endswith('"'):
                        clean_value = clean_value[1:-1]
                clean_row[clean_key] = clean_value
            
            if clean_row.get('Nama Instansi') and clean_row.get('Nama Paket'):
                data.append(clean_row)
    
    print(f"✅ Parsed {len(data)} records")
    return data


async def import_data(data: list):
    """Import data to database"""
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT COUNT(*) FROM rup_paket_detailed"))
        existing = result.scalar()
        print(f"📊 Existing records: {existing}")
        
        if existing > 0:
            response = input(f"⚠️ Found {existing} records. Append? (y/n): ")
            if response.lower() != 'y':
                print("❌ Aborted")
                return
        
        imported = 0
        errors = 0
        
        for row in data:
            total_nilai = None
            total_str = row.get('Total Nilai (Rp)')
            if total_str:
                try:
                    total_nilai = float(total_str.replace(',', '').replace('"', ''))
                except:
                    errors += 1
            
            nilai_pdn = None
            pdn_str = row.get('Nilai PDN (Rp)')
            if pdn_str:
                try:
                    nilai_pdn = float(pdn_str.replace(',', '').replace('"', ''))
                except:
                    pass
            
            tahun = None
            tahun_str = row.get('Tahun Anggaran')
            if tahun_str:
                try:
                    tahun = int(tahun_str)
                except:
                    pass
            
            try:
                await session.execute(text("""
                    INSERT INTO rup_paket_detailed (
                        kode_paket, kode_rup, tahun_anggaran,
                        nama_instansi, satuan_kerja, nama_penyedia,
                        nama_paket, total_nilai, nilai_pdn,
                        sumber_transaksi, sumber_dana, metode_pengadaan,
                        jenis_pengadaan, status_paket
                    ) VALUES (
                        :kode_paket, :kode_rup, :tahun,
                        :instansi, :satuan_kerja, :penyedia,
                        :paket, :total, :pdn,
                        :sumber_transaksi, :sumber_dana, :metode,
                        :jenis, :status
                    )
                """), {
                    'kode_paket': row.get('Kode Paket'),
                    'kode_rup': row.get('Kode RUP'),
                    'tahun': tahun,
                    'instansi': row.get('Nama Instansi'),
                    'satuan_kerja': row.get('Nama Satuan Kerja'),
                    'penyedia': row.get('Nama Penyedia'),
                    'paket': row.get('Nama Paket'),
                    'total': total_nilai,
                    'pdn': nilai_pdn,
                    'sumber_transaksi': row.get('Sumber Transaksi'),
                    'sumber_dana': row.get('Sumber Dana'),
                    'metode': row.get('Metode Pengadaan'),
                    'jenis': row.get('Jenis Pengadaan'),
                    'status': row.get('Status Paket')
                })
                
                imported += 1
                
                if imported % 500 == 0:
                    await session.commit()
                    print(f"   Imported {imported} records...")
                    
            except Exception as e:
                errors += 1
                if errors <= 10:
                    print(f"   ⚠️ Error: {e}")
        
        await session.commit()
        
        print(f"\n✅ Imported: {imported} records")
        if errors > 0:
            print(f"⚠️ Errors: {errors} records")


async def verify_import():
    """Verify import results"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT COUNT(*) FROM rup_paket_detailed"))
        total = result.scalar()
        
        result = await session.execute(text("""
            SELECT tahun_anggaran, COUNT(*) 
            FROM rup_paket_detailed 
            WHERE tahun_anggaran IS NOT NULL
            GROUP BY tahun_anggaran 
            ORDER BY tahun_anggaran
        """))
        
        print("\n📊 IMPORT SUMMARY:")
        print(f"   Total records: {total}")
        print("   By year:")
        for row in result:
            print(f"      {row[0]}: {row[1]} records")
        
        result = await session.execute(text("""
            SELECT 
                COUNT(DISTINCT nama_penyedia) as unique_vendors,
                COUNT(DISTINCT nama_instansi) as unique_instansi
            FROM rup_paket_detailed
        """))
        row = result.first()
        if row:
            print(f"\n🏢 UNIQUE ENTITIES:")
            print(f"   Vendors: {row[0]}")
            print(f"   Institutions: {row[1]}")
        
        result = await session.execute(text("""
            SELECT nama_penyedia, total_nilai, tahun_anggaran 
            FROM rup_paket_detailed 
            WHERE nama_penyedia IS NOT NULL AND total_nilai > 0
            ORDER BY total_nilai DESC
            LIMIT 5
        """))
        print("\n💰 TOP 5 CONTRACTS:")
        for row in result:
            print(f"   {row[0]}: Rp{row[1]:,.0f} ({row[2]})")


async def main():
    print("=" * 60)
    print("ETL: CSV RUP to rup_paket_detailed")
    print("=" * 60)
    print()
    
    file_path = "/app/RUP_data_realisasi_2022_2026.csv"
    
    if not Path(file_path).exists():
        print(f"❌ File not found: {file_path}")
        return
    
    print(f"📁 File: {file_path}")
    
    data = parse_rup_csv(file_path)
    
    if not data:
        print("❌ No valid data found")
        return
    
    print("\n📋 SAMPLE RECORD:")
    sample = data[0]
    for key in ['Nama Instansi', 'Nama Penyedia', 'Tahun Anggaran', 'Total Nilai (Rp)']:
        print(f"   {key}: {sample.get(key, 'N/A')}")
    
    print()
    
    await import_data(data)
    await verify_import()
    
    print("\n" + "=" * 60)
    print("✅ ETL COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())