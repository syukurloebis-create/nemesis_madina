#!/usr/bin/env python
# scripts/upload_rup_batch.py
import pandas as pd
import requests
import time
import json
import sys
from pathlib import Path

# Konfigurasi
API_URL = "http://localhost:8001/federation/ingest/partner_a"
API_KEY = "secret-key-123"
DELAY = 0.5  # delay antar request (detik)

def load_excel_data(file_path):
    """Load data from Excel file"""
    df = pd.read_excel(file_path, sheet_name='2026')
    print(f"📊 Loaded {len(df)} rows from {file_path}")
    return df

def upload_package(row, index):
    """Upload satu paket ke NEMESIS"""
    try:
        # Generate aggregate_id dari nomor_id atau index
        nomor_id = str(row.get('nomor_id', f"rup-{index}"))
        aggregate_id = f"rup-{nomor_id}" if nomor_id else f"rup-{index:05d}"
        
        # Prepare payload
        payload = {
            "type": "procurement.package.created",
            "aggregate_id": aggregate_id,
            "correlation_id": f"rup-batch-{index}",
            "data": {
                "nama_paket": str(row.get('nama_paket', 'Unknown'))[:200],
                "pagu": float(row.get('pagu', 0)) if pd.notna(row.get('pagu')) else 0,
                "jenis": str(row.get('jenis', 'Barang')),
                "kategori": str(row.get('kategori', 'Unknown')),
                "metode": str(row.get('metode', 'Unknown')),
                "bulan": str(row.get('bulan', 'Unknown')),
                "lokasi": str(row.get('lokasi', 'Mandailing Natal')),
                "instansi": str(row.get('instansi', 'Unknown')),
            }
        }
        
        # Send request
        response = requests.post(
            API_URL,
            json=payload,
            headers={"X-API-Key": API_KEY},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ [{index}] Uploaded: {aggregate_id} - {payload['data']['nama_paket'][:40]}...")
            return True
        else:
            print(f"❌ [{index}] Failed: {response.status_code} - {response.text[:100]}")
            return False
            
    except Exception as e:
        print(f"❌ [{index}] Error: {str(e)[:100]}")
        return False

def main():
    # Cek file Excel
    excel_path = Path("RUP MADINA 2026.xlsx")
    if not excel_path.exists():
        print("❌ File 'RUP MADINA 2026.xlsx' not found in current directory")
        print("   Please place the file in the project root directory")
        sys.exit(1)
    
    print("🚀 Starting batch upload of RUP MADINA 2026 data...")
    print("=" * 60)
    
    # Load data
    df = load_excel_data(excel_path)
    
    # Preview first 5 rows
    print("\n📋 Preview first 5 rows:")
    print(df[['nama_paket', 'pagu', 'instansi', 'metode']].head())
    print("=" * 60)
    
    # Confirm
    response = input(f"\n⚠️  Upload {len(df)} procurement packages? (y/n): ")
    if response.lower() != 'y':
        print("❌ Upload cancelled")
        return
    
    print("\n📤 Starting upload...")
    print("-" * 60)
    
    # Upload each row
    success_count = 0
    fail_count = 0
    start_time = time.time()
    
    for idx, row in df.iterrows():
        success = upload_package(row, idx + 1)
        if success:
            success_count += 1
        else:
            fail_count += 1
        time.sleep(DELAY)
        
        # Progress indicator
        if (idx + 1) % 50 == 0:
            print(f"📊 Progress: {idx + 1}/{len(df)} packages uploaded")
    
    # Summary
    elapsed = time.time() - start_time
    print("\n" + "=" * 60)
    print("📊 UPLOAD SUMMARY")
    print(f"   Total packages: {len(df)}")
    print(f"   ✅ Success: {success_count}")
    print(f"   ❌ Failed: {fail_count}")
    print(f"   ⏱️  Time: {elapsed:.1f} seconds")
    print("=" * 60)
    
    # Verification suggestion
    if success_count > 0:
        print("\n🔍 To verify, run:")
        print("   curl http://localhost:8001/event_lineage/?limit=20")
        print("   curl http://localhost:8001/anomalies/?limit=10")
        print("   curl http://localhost:8001/intelligence/dashboard/risk-leaders?limit=10")

if __name__ == "__main__":
    main()
