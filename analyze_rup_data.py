"""
Analisis Data RUP - Vendor Intelligence
Run this on LOCAL Windows
"""

import pandas as pd
import os

# Load data
df = pd.read_csv('rup_paket_detailed.csv')
print("=" * 60)
print("RUP DATA ANALYSIS - VENDOR INTELLIGENCE")
print("=" * 60)
print()

# Basic statistics
print("📊 BASIC STATISTICS:")
print(f"   Total records: {len(df)}")
print(f"   Unique vendors: {df['nama_penyedia'].nunique()}")
print(f"   Unique institutions: {df['nama_instansi'].nunique()}")
print()

# Distribution by year
print("📅 DISTRIBUTION BY YEAR:")
year_counts = df['tahun_anggaran'].value_counts().sort_index()
for year, count in year_counts.items():
    print(f"   {year}: {count} packages")
print()

# Top vendors by package count
print("🏆 TOP 15 VENDORS BY PACKAGE COUNT:")
vendor_counts = df.groupby('nama_penyedia').size().sort_values(ascending=False).head(15)
for vendor, count in vendor_counts.items():
    total_value = df[df['nama_penyedia'] == vendor]['total_nilai'].sum()
    print(f"   {vendor}: {count} packages (Rp{total_value:,.0f})")
print()

# Top vendors by total value
print("💰 TOP 10 VENDORS BY TOTAL VALUE:")
vendor_value = df.groupby('nama_penyedia')['total_nilai'].sum().sort_values(ascending=False).head(10)
for vendor, value in vendor_value.items():
    package_count = df[df['nama_penyedia'] == vendor].shape[0]
    print(f"   {vendor}: Rp{value:,.0f} ({package_count} packages)")
print()

# Vendor collusion detection (shared institutions)
print("🤝 VENDOR COLLABORATION DETECTION:")
institution_vendors = df.groupby('nama_instansi')['nama_penyedia'].apply(lambda x: list(set(x))).to_dict()

vendor_pairs = {}
for institution, vendors in institution_vendors.items():
    vendors = [v for v in vendors if pd.notna(v)]
    if len(vendors) >= 2:
        for i in range(len(vendors)):
            for j in range(i+1, len(vendors)):
                v1, v2 = sorted([vendors[i], vendors[j]])
                key = (v1, v2)
                vendor_pairs[key] = vendor_pairs.get(key, 0) + 1

suspicious_pairs = [(v1, v2, count) for (v1, v2), count in vendor_pairs.items() if count >= 3]
suspicious_pairs.sort(key=lambda x: x[2], reverse=True)

if suspicious_pairs:
    print(f"   Found {len(suspicious_pairs)} suspicious vendor pairs (shared >=3 institutions):")
    for v1, v2, count in suspicious_pairs[:10]:
        print(f"   - {v1} <-> {v2}: {count} shared institutions")
else:
    print("   No suspicious vendor pairs found")
print()

# Procurement method distribution
print("📋 PROCUREMENT METHOD DISTRIBUTION:")
method_counts = df['metode_pengadaan'].value_counts().head(10)
for method, count in method_counts.items():
    print(f"   {method}: {count} packages")
print()

# Status distribution
print("✅ STATUS DISTRIBUTION:")
status_counts = df['status_paket'].value_counts().head(10)
for status, count in status_counts.items():
    print(f"   {status}: {count} packages")
print()

print("=" * 60)
print("✅ ANALYSIS COMPLETE")
print("=" * 60)