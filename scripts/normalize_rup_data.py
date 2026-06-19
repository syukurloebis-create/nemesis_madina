#!/usr/bin/env python3
"""
Normalisasi Data RUP (Rencana Umum Pengadaan)
Membaca file Excel RUP 2025 dan 2026, melakukan standardisasi data,
dan menyimpan hasil yang sudah dinormalisasi.
"""

import pandas as pd
import re
import os
from datetime import datetime

# =========================================================
# KONFIGURASI
# =========================================================

INPUT_FILE_2026 = "RUP MADINA 2026.xlsx"
INPUT_FILE_2025 = "RUP Penyedia 2025.xlsx"
OUTPUT_FILE = "RUP_NORMALIZED.xlsx"

# =========================================================
# MAPPING STANDARDISASI
# =========================================================

# 1. Mapping Jenis Pengadaan
JENIS_MAPPING = {
    'Barang': 'BARANG',
    'barang': 'BARANG',
    'BARANG': 'BARANG',
    'Jasa Konsultansi': 'JASA_KONSULTANSI',
    'Jasa Konsultansi ': 'JASA_KONSULTANSI',
    'jasa konsultansi': 'JASA_KONSULTANSI',
    'Jasa Lainnya': 'JASA_LAINNYA',
    'Jasa Lainnya ': 'JASA_LAINNYA',
    'jasa lainnya': 'JASA_LAINNYA',
    'Pekerjaan Konstruksi': 'PEKERJAAN_KONSTRUKSI',
    'Pekerjaan Konstruksi ': 'PEKERJAAN_KONSTRUKSI',
    'pekerjaan konstruksi': 'PEKERJAAN_KONSTRUKSI',
}

# 2. Mapping Kategori Usaha
KATEGORI_MAPPING = {
    'Usaha Kecil Koperasi': 'UKM_KOPERASI',
    'Usaha Kecil Koperasi ': 'UKM_KOPERASI',
    'Bukan Usaha Kecil Koperasi': 'NON_UKM',
    'Bukan Usaha Kecil Koperasi ': 'NON_UKM',
}

# 3. Mapping Metode Pengadaan
METODE_MAPPING = {
    'Pengadaan Langsung': 'PENGADAAN_LANGSUNG',
    'Pengadaan Langsung ': 'PENGADAAN_LANGSUNG',
    'E Purchasing': 'E_PURCHASING',
    'E Purchasing ': 'E_PURCHASING',
    'Dikecualikan': 'DIKECUALIKAN',
    'Dikecualikan ': 'DIKECUALIKAN',
    'Penunjukan Langsung': 'PENUNJUKAN_LANGSUNG',
    'Penunjukan Langsung ': 'PENUNJUKAN_LANGSUNG',
    'Seleksi': 'SELEKSI',
    'Seleksi ': 'SELEKSI',
    'Tender': 'TENDER',
    'Tender ': 'TENDER',
    'Tender Cepat': 'TENDER_CEPAT',
}

# 4. Mapping Bulan
BULAN_MAPPING = {
    'January 2025': '2025-01',
    'January 2026': '2026-01',
    'January 2024': '2024-01',
    'January 2020': '2020-01',
    'February 2025': '2025-02',
    'February 2026': '2026-02',
    'March 2025': '2025-03',
    'March 2026': '2026-03',
    'April 2025': '2025-04',
    'April 2026': '2026-04',
    'May 2025': '2025-05',
    'May 2026': '2026-05',
    'June 2025': '2025-06',
    'June 2026': '2026-06',
    'July 2025': '2025-07',
    'July 2026': '2026-07',
    'August 2025': '2025-08',
    'August 2026': '2026-08',
    'September 2025': '2025-09',
    'September 2026': '2026-09',
    'October 2025': '2025-10',
    'October 2026': '2026-10',
    'November 2025': '2025-11',
    'November 2026': '2026-11',
    'December 2025': '2025-12',
    'December 2026': '2026-12',
}

# 5. Mapping Instansi
INSTANSI_MAPPING = {
    # Dinas-dinas
    'DINAS KESEHATAN': 'DINAS_KESEHATAN',
    'Dinas Kesehatan': 'DINAS_KESEHATAN',
    'DINAS PENDIDIKAN DAN KEBUDAYAAN': 'DINAS_PENDIDIKAN_DAN_KEBUDAYAAN',
    'Dinas Pendidikan dan Kebudayaan': 'DINAS_PENDIDIKAN_DAN_KEBUDAYAAN',
    'DINAS PERHUBUNGAN': 'DINAS_PERHUBUNGAN',
    'Dinas Perhubungan': 'DINAS_PERHUBUNGAN',
    'DINAS PERTANIAN': 'DINAS_PERTANIAN',
    'Dinas Pertanian': 'DINAS_PERTANIAN',
    'DINAS PERDAGANGAN': 'DINAS_PERDAGANGAN',
    'Dinas Perdagangan': 'DINAS_PERDAGANGAN',
    'DINAS PERUMAHAN RAKYAT DAN KAWASAN PERMUKIMAN SERTA PERTANAHAN': 'DINAS_PERUMAHAN_RAKYAT',
    'Dinas Perumahan Rakyat dan Kawasan Permukiman serta Pertanahan': 'DINAS_PERUMAHAN_RAKYAT',
    'DINAS PEKERJAAN UMUM DAN PENATAAN RUANG': 'DINAS_PUPR',
    'Dinas Pekerjaan Umum dan Penataan Ruang': 'DINAS_PUPR',
    'DINAS LINGKUNGAN HIDUP': 'DINAS_LINGKUNGAN_HIDUP',
    'Dinas Lingkungan Hidup': 'DINAS_LINGKUNGAN_HIDUP',
    'DINAS KEPENDUDUKAN DAN PENCATATAN SIPIL': 'DINAS_DUKCAPIL',
    'Dinas Kependudukan dan Pencatatan Sipil': 'DINAS_DUKCAPIL',
    'DINAS SOSIAL PEMBERDAYAAN PEREMPUAN DAN PERLINDUNGAN ANAK': 'DINAS_SOSIAL_P3A',
    'Dinas Sosial Pemberdayaan Perempuan dan Perlindungan Anak': 'DINAS_SOSIAL_P3A',
    'DINAS PEMBERDAYAAN MASYARAKAT DAN DESA': 'DINAS_PMD',
    'Dinas Pemberdayaan Masyarakat dan Desa': 'DINAS_PMD',
    'DINAS PERIKANAN': 'DINAS_PERIKANAN',
    'Dinas Perikanan': 'DINAS_PERIKANAN',
    'DINAS KOPERASI USAHA KECIL DAN MENENGAH': 'DINAS_KOPERASI_UKM',
    'Dinas Koperasi Usaha Kecil dan Menengah': 'DINAS_KOPERASI_UKM',
    'DINAS PARIWISATA': 'DINAS_PARIWISATA',
    'Dinas Pariwisata': 'DINAS_PARIWISATA',
    'DINAS PENANAMAN MODAL DAN PELAYANAN TERPADU SATU PINTU': 'DINAS_PMPTSP',
    'Dinas Penanaman Modal dan Pelayanan Terpadu Satu Pintu': 'DINAS_PMPTSP',
    'DINAS TENAGA KERJA': 'DINAS_TENAGA_KERJA',
    'Dinas Tenaga Kerja': 'DINAS_TENAGA_KERJA',
    'DINAS KOMUNIKASI DAN INFORMATIKA': 'DINAS_KOMINFO',
    'Dinas Komunikasi dan Informatika': 'DINAS_KOMINFO',
    'DINAS KETAHANAN PANGAN': 'DINAS_KETAHANAN_PANGAN',
    'Dinas Ketahanan Pangan': 'DINAS_KETAHANAN_PANGAN',
    'DINAS PERPUSTAKAAN DAN KEARSIPAN': 'DINAS_PERPUTAKAAN',
    'Dinas Perpustakaan dan Kearsipan': 'DINAS_PERPUTAKAAN',
    'DINAS PENGENDALIAN PENDUDUK DAN KELUARGA BERENCANA': 'DINAS_PPKB',
    'Dinas Pengendalian Penduduk dan Keluarga Berencana': 'DINAS_PPKB',
    'DINAS PEMUDA DAN OLAHRAGA': 'DINAS_PEMUDA_OLAHRAGA',
    'Dinas Pemuda dan Olahraga': 'DINAS_PEMUDA_OLAHRAGA',
    
    # Badan-badan
    'BADAN PENDAPATAN DAERAH': 'BADAN_PENDAPATAN_DAERAH',
    'Badan Pendapatan Daerah': 'BADAN_PENDAPATAN_DAERAH',
    'BADAN PENGELOLAAN KEUANGAN DAN ASET DAERAH': 'BADAN_PENGELOLAAN_KEUANGAN_ASET',
    'Badan Pengelolaan Keuangan dan Aset Daerah': 'BADAN_PENGELOLAAN_KEUANGAN_ASET',
    'BADAN PERENCANAAN PEMBANGUNAN RISET DAN INOVASI DAERAH': 'BADAN_PERENCANAAN_PEMBANGUNAN',
    'Badan Perencanaan Pembangunan Riset dan Inovasi Daerah': 'BADAN_PERENCANAAN_PEMBANGUNAN',
    'BADAN KESATUAN BANGSA DAN POLITIK': 'BADAN_KESBANGPOL',
    'Badan Kesatuan Bangsa dan Politik': 'BADAN_KESBANGPOL',
    'BADAN PENANGGULANGAN BENCANA DAERAH': 'BADAN_PBBD',
    'Badan Penanggulangan Bencana Daerah': 'BADAN_PBBD',
    'BADAN KEPEGAWAIAN DAN PENGEMBANGAN SUMBER DAYA MANUSIA': 'BADAN_KEUANGAN_SDM',
    'Badan Kepegawaian dan Pengembangan Sumber Daya Manusia': 'BADAN_KEUANGAN_SDM',
    
    # Sekretariat
    'SEKRETARIAT DAERAH KABUPATEN': 'SEKRETARIAT_DAERAH',
    'Sekretariat Daerah Kabupaten': 'SEKRETARIAT_DAERAH',
    'SEKRETARIAT DPRD': 'SEKRETARIAT_DPRD',
    'Sekretariat DPRD': 'SEKRETARIAT_DPRD',
    
    # Lainnya
    'INSPEKTORAT DAERAH KABUPATEN': 'INSPEKTORAT_DAERAH',
    'Inspektorat Daerah Kabupaten': 'INSPEKTORAT_DAERAH',
    'SATUAN POLISI PAMONG PRAJA DAN PEMADAM KEBAKARAN': 'SATPOL_PP_DAMKAR',
    'Satuan Polisi Pamong Praja dan Pemadam Kebakaran': 'SATPOL_PP_DAMKAR',
    'RUMAH SAKIT UMUM DAERAH PANYABUNGAN': 'RSUD_PANYABUNGAN',
    'Rumah Sakit Umum Daerah Panyabungan': 'RSUD_PANYABUNGAN',
    'RUMAH SAKIT UMUM DAERAH dr. HUSNI THAMRIN': 'RSUD_DR_HUSNI_THAMRIN',
    'Rumah Sakit Umum Daerah dr. Husni Thamrin': 'RSUD_DR_HUSNI_THAMRIN',
    
    # Bagian-bagian
    'BAGIAN UMUM': 'BAGIAN_UMUM',
    'Bagian Umum': 'BAGIAN_UMUM',
    'BAGIAN KESEJAHTERAAN RAKYAT': 'BAGIAN_KESRA',
    'Bagian Kesejahteraan Rakyat': 'BAGIAN_KESRA',
    'BAGIAN PEREKONOMIAN DAN SUMBER DAYA ALAM': 'BAGIAN_PEREKONOMIAN',
    'Bagian Perekonomian dan Sumber Daya Alam': 'BAGIAN_PEREKONOMIAN',
    'BAGIAN TATA PEMERINTAHAN': 'BAGIAN_TATA_PEMERINTAHAN',
    'Bagian Tata Pemerintahan': 'BAGIAN_TATA_PEMERINTAHAN',
    'BAGIAN HUKUM': 'BAGIAN_HUKUM',
    'Bagian Hukum': 'BAGIAN_HUKUM',
    'BAGIAN ORGANISASI': 'BAGIAN_ORGANISASI',
    'Bagian Organisasi': 'BAGIAN_ORGANISASI',
    'BAGIAN PROTOKOL DAN KOMUNIKASI PIMPINAN': 'BAGIAN_PROTOKOL',
    'Bagian Protokol dan Komunikasi Pimpinan': 'BAGIAN_PROTOKOL',
    'BAGIAN ADMINISTRASI PEMBANGUNAN': 'BAGIAN_ADMINISTRASI_PEMBANGUNAN',
    'Bagian Administrasi Pembangunan': 'BAGIAN_ADMINISTRASI_PEMBANGUNAN',
    'BAGIAN PENGADAAN BARANG DAN JASA': 'BAGIAN_PENGADAAN',
    'Bagian Pengadaan Barang dan Jasa': 'BAGIAN_PENGADAAN',
    
    # Kecamatan
    'KECAMATAN PUNCAK SORIK MARAPI': 'KECAMATAN_PUNCAK_SORIK_MARAPI',
    'KECAMATAN PANYABUNGAN': 'KECAMATAN_PANYABUNGAN',
    'KECAMATAN LEMBAH SORIK MARAPI': 'KECAMATAN_LEMBAH_SORIK_MARAPI',
    'KECAMATAN ULU PUNGKUT': 'KECAMATAN_ULU_PUNGKUT',
    'KECAMATAN PAKANTAN': 'KECAMATAN_PAKANTAN',
    'KECAMATAN SIABU': 'KECAMATAN_SIABU',
    'KECAMATAN BATAHAN': 'KECAMATAN_BATAHAN',
    'KECAMATAN BUKIT MALINTANG': 'KECAMATAN_BUKIT_MALINTANG',
    'KECAMATAN HUTABARGOT': 'KECAMATAN_HUTABARGOT',
    'KECAMATAN TAMBANGAN': 'KECAMATAN_TAMBANGAN',
    'KECAMATAN SINUNUKAN': 'KECAMATAN_SINUNUKAN',
    'KECAMATAN KOTANOPAN': 'KECAMATAN_KOTANOPAN',
    'KECAMATAN NATAL': 'KECAMATAN_NATAL',
    'KECAMATAN BATANG NATAL': 'KECAMATAN_BATANG_NATAL',
    'KECAMATAN MUARA BATANG GADIS': 'KECAMATAN_MUARA_BATANG_GADIS',
    'KECAMATAN LINGGA BAYU': 'KECAMATAN_LINGGA_BAYU',
    'KECAMATAN RANTO BAEK': 'KECAMATAN_RANTO_BAEK',
    'KECAMATAN PANYABUNGAN BARAT': 'KECAMATAN_PANYABUNGAN_BARAT',
    'KECAMATAN PANYABUNGAN SELATAN': 'KECAMATAN_PANYABUNGAN_SELATAN',
    'KECAMATAN PANYABUNGAN TIMUR': 'KECAMATAN_PANYABUNGAN_TIMUR',
    'KECAMATAN PANYABUNGAN UTARA': 'KECAMATAN_PANYABUNGAN_UTARA',
    'KECAMATAN NAGA JUANG': 'KECAMATAN_NAGA_JUANG',
    'KECAMATAN MUARASIPONGI': 'KECAMATAN_MUARASIPONGI',
}

# =========================================================
# FUNGSI BANTU
# =========================================================

def convert_pagu(value):
    """Konversi nilai pagu ke integer"""
    if pd.isna(value):
        return 0
    if isinstance(value, (int, float)):
        return int(value)
    # Hapus titik dan koma, konversi ke integer
    cleaned = str(value).replace(',', '').replace('.', '')
    if cleaned.isdigit():
        return int(cleaned)
    return 0

def standardize_instansi(instansi):
    """Standardisasi nama instansi"""
    if pd.isna(instansi):
        return None
    # Coba mapping langsung
    instansi_str = str(instansi).strip()
    if instansi_str in INSTANSI_MAPPING:
        return INSTANSI_MAPPING[instansi_str]
    # Coba dengan upper case
    instansi_upper = instansi_str.upper()
    if instansi_upper in INSTANSI_MAPPING:
        return INSTANSI_MAPPING[instansi_upper]
    # Jika tidak ditemukan, return asli dengan format standar
    return instansi_upper.replace(' ', '_').replace('.', '')

def normalize_dataframe(df, tahun_label):
    """Normalisasi dataframe"""
    df_normalized = df.copy()
    
    # Standardisasi jenis
    df_normalized['jenis_normalized'] = df_normalized['jenis'].map(JENIS_MAPPING)
    
    # Standardisasi kategori
    df_normalized['kategori_normalized'] = df_normalized['kategori'].map(KATEGORI_MAPPING)
    
    # Standardisasi metode
    df_normalized['metode_normalized'] = df_normalized['metode'].map(METODE_MAPPING)
    
    # Standardisasi bulan
    df_normalized['bulan_normalized'] = df_normalized['bulan'].map(BULAN_MAPPING)
    
    # Ekstrak tahun
    df_normalized['tahun'] = tahun_label
    
    # Konversi pagu
    df_normalized['pagu_numeric'] = df_normalized['pagu'].apply(convert_pagu)
    
    # Standardisasi instansi
    df_normalized['instansi_normalized'] = df_normalized['instansi'].apply(standardize_instansi)
    
    return df_normalized

# =========================================================
# EKSEKUSI UTAMA
# =========================================================

def main():
    print("=" * 70)
    print("NORMALISASI DATA RUP")
    print("=" * 70)
    
    # Baca file Excel
    print("\n📂 Membaca file Excel...")
    
    # File 2026
    df_2026 = pd.read_excel(INPUT_FILE_2026, sheet_name='2026')
    print(f"   ✅ Data 2026: {len(df_2026)} baris")
    
    # File 2025
    df_2025 = pd.read_excel(INPUT_FILE_2025, sheet_name='Sheet1')
    print(f"   ✅ Data 2025: {len(df_2025)} baris")
    
    # Normalisasi data
    print("\n🔄 Normalisasi data...")
    df_2026_norm = normalize_dataframe(df_2026, 2026)
    df_2025_norm = normalize_dataframe(df_2025, 2025)
    print("   ✅ Normalisasi selesai")
    
    # Simpan ke file Excel
    print(f"\n💾 Menyimpan ke {OUTPUT_FILE}...")
    
    with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl') as writer:
        # Sheet 2026 - Data lengkap
        df_2026_norm.to_excel(writer, sheet_name='2026_RAW', index=False)
        
        # Sheet 2026 - Normalized only
        cols_2026 = ['nama_paket', 'pagu_numeric', 'jenis_normalized', 'tahun', 
                     'bulan_normalized', 'kategori_normalized', 'metode_normalized', 
                     'lokasi', 'instansi_normalized', 'nomor_id']
        df_2026_norm[cols_2026].to_excel(writer, sheet_name='2026_NORMALIZED', index=False)
        
        # Sheet 2025 - Data lengkap
        df_2025_norm.to_excel(writer, sheet_name='2025_RAW', index=False)
        
        # Sheet 2025 - Normalized only
        cols_2025 = ['nama_paket', 'pagu_numeric', 'jenis_normalized', 'tahun', 
                     'bulan_normalized', 'kategori_normalized', 'metode_normalized', 
                     'lokasi', 'instansi_normalized', 'nomor_id']
        df_2025_norm[cols_2025].to_excel(writer, sheet_name='2025_NORMALIZED', index=False)
    
    print("   ✅ File disimpan")
    
    # Statistik
    print("\n" + "=" * 70)
    print("📊 STATISTIK NORMALISASI")
    print("=" * 70)
    
    print("\n=== DATA 2026 ===")
    print(f"   Total paket: {len(df_2026_norm)}")
    print(f"   Total pagu: Rp {df_2026_norm['pagu_numeric'].sum():,.0f}")
    print(f"\n   Distribusi Jenis:")
    for jenis, count in df_2026_norm['jenis_normalized'].value_counts().items():
        print(f"      - {jenis}: {count} paket")
    print(f"\n   Distribusi Metode:")
    for metode, count in df_2026_norm['metode_normalized'].value_counts().items():
        print(f"      - {metode}: {count} paket")
    print(f"\n   Top 5 Instansi:")
    for instansi, count in df_2026_norm['instansi_normalized'].value_counts().head(5).items():
        print(f"      - {instansi}: {count} paket")
    
    print("\n=== DATA 2025 ===")
    print(f"   Total paket: {len(df_2025_norm)}")
    print(f"   Total pagu: Rp {df_2025_norm['pagu_numeric'].sum():,.0f}")
    print(f"\n   Distribusi Jenis:")
    for jenis, count in df_2025_norm['jenis_normalized'].value_counts().items():
        print(f"      - {jenis}: {count} paket")
    print(f"\n   Distribusi Metode:")
    for metode, count in df_2025_norm['metode_normalized'].value_counts().items():
        print(f"      - {metode}: {count} paket")
    print(f"\n   Top 5 Instansi:")
    for instansi, count in df_2025_norm['instansi_normalized'].value_counts().head(5).items():
        print(f"      - {instansi}: {count} paket")
    
    print("\n" + "=" * 70)
    print("✅ NORMALISASI SELESAI!")
    print("=" * 70)
    print(f"\n📁 Output file: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
