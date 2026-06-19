#!/usr/bin/env python3
"""
Analisis Risiko Pengadaan RUP
Mendeteksi anomali pada nilai, metode, dan instansi
"""

import pandas as pd
import psycopg2
from sqlalchemy import create_engine, text
import numpy as np
from datetime import datetime

DATABASE_URL = "postgresql://nemesis:nemesis123@localhost:5432/nemesis_db"

# =========================================================
# FUNGSI ANALISIS
# =========================================================

def detect_high_value_anomalies(engine):
    """Deteksi paket dengan nilai di atas rata-rata + 3 standar deviasi"""
    
    query = text("""
        WITH stats AS (
            SELECT 
                AVG(pagu) as mean_pagu,
                STDDEV(pagu) as stddev_pagu
            FROM rup_paket
            WHERE pagu > 0
        )
        SELECT 
            r.id,
            r.nama_paket,
            r.instansi,
            r.jenis,
            r.metode,
            r.pagu,
            r.tahun,
            s.mean_pagu,
            s.stddev_pagu,
            (r.pagu - s.mean_pagu) / NULLIF(s.stddev_pagu, 0) as z_score
        FROM rup_paket r, stats s
        WHERE r.pagu > 0
        AND r.pagu > s.mean_pagu + 3 * s.stddev_pagu
        ORDER BY r.pagu DESC
        LIMIT 30
    """)
    
    df = pd.read_sql(query, engine)
    return df

def detect_method_anomalies(engine):
    """Deteksi metode pengadaan yang tidak biasa untuk nilai besar"""
    
    query = text("""
        SELECT 
            metode,
            COUNT(*) as total_paket,
            MIN(pagu) as min_pagu,
            AVG(pagu) as avg_pagu,
            MAX(pagu) as max_pagu,
            SUM(pagu) as total_pagu,
            -- Rasio metode yang tidak umum untuk nilai besar
            SUM(CASE WHEN pagu > 1000000000 THEN 1 ELSE 0 END) as paket_miliar,
            SUM(CASE WHEN pagu > 5000000000 THEN 1 ELSE 0 END) as paket_lima_miliar
        FROM rup_paket
        WHERE pagu > 0
        GROUP BY metode
        ORDER BY total_pagu DESC
    """)
    
    return pd.read_sql(query, engine)

def detect_instansi_anomalies(engine):
    """Deteksi instansi dengan pola pengadaan tidak biasa"""
    
    query = text("""
        SELECT 
            instansi,
            COUNT(*) as total_paket,
            AVG(pagu) as avg_pagu,
            SUM(pagu) as total_pagu,
            -- Variasi metode
            COUNT(DISTINCT metode) as metode_count,
            -- Konsentrasi ke satu metode
            MODE() WITHIN GROUP (ORDER BY metode) as metode_dominan,
            COUNT(*) FILTER (WHERE metode = 'PENGADAAN_LANGSUNG') as paket_pl,
            COUNT(*) FILTER (WHERE metode = 'E_PURCHASING') as paket_ep,
            COUNT(*) FILTER (WHERE metode = 'TENDER') as paket_tender,
            -- Nilai ekstrem
            MAX(pagu) as max_pagu,
            MIN(pagu) as min_pagu
        FROM rup_paket
        GROUP BY instansi
        HAVING COUNT(*) >= 5
        ORDER BY total_pagu DESC
        LIMIT 30
    """)
    
    return pd.read_sql(query, engine)

def detect_duplicate_suspicions(engine):
    """Deteksi paket yang mencurigakan (nama mirip, nilai mirip, instansi sama)"""
    
    query = text("""
        SELECT 
            a.id as id1,
            b.id as id2,
            a.nama_paket as paket1,
            b.nama_paket as paket2,
            a.instansi,
            a.pagu as pagu1,
            b.pagu as pagu2,
            ABS(a.pagu - b.pagu) as selisih_pagu,
            a.tahun as tahun1,
            b.tahun as tahun2,
            a.metode as metode1,
            b.metode as metode2
        FROM rup_paket a
        JOIN rup_paket b ON a.instansi = b.instansi 
            AND a.id < b.id
            AND a.tahun = b.tahun
            AND ABS(a.pagu - b.pagu) < a.pagu * 0.1
            AND a.pagu > 500000000
        WHERE a.nama_paket != b.nama_paket
        ORDER BY a.pagu DESC
        LIMIT 20
    """)
    
    return pd.read_sql(query, engine)

def detect_seasonal_anomalies(engine):
    """Deteksi lonjakan pengadaan di bulan-bulan tertentu"""
    
    query = text("""
        SELECT 
            tahun,
            EXTRACT(MONTH FROM bulan) as bulan,
            COUNT(*) as total_paket,
            SUM(pagu) as total_pagu,
            AVG(pagu) as avg_pagu,
            -- Bandingkan dengan rata-rata tahunan
            SUM(pagu) / NULLIF(SUM(SUM(pagu)) OVER (PARTITION BY tahun), 0) * 100 as persentase_tahunan
        FROM rup_paket
        WHERE bulan IS NOT NULL
        GROUP BY tahun, EXTRACT(MONTH FROM bulan)
        ORDER BY tahun, bulan
    """)
    
    return pd.read_sql(query, engine)

def detect_single_bidder_risk(engine):
    """Deteksi metode yang berisiko (Pengadaan Langsung untuk nilai besar)"""
    
    query = text("""
        SELECT 
            instansi,
            COUNT(*) as total_paket_pl,
            SUM(pagu) as total_pagu_pl,
            AVG(pagu) as avg_pagu_pl,
            MAX(pagu) as max_pagu_pl,
            -- Paket PL di atas 500 juta
            COUNT(*) FILTER (WHERE pagu > 500000000) as paket_pl_diatas_500jt,
            SUM(pagu) FILTER (WHERE pagu > 500000000) as total_pl_diatas_500jt
        FROM rup_paket
        WHERE metode = 'PENGADAAN_LANGSUNG'
        GROUP BY instansi
        HAVING SUM(pagu) > 1000000000
        ORDER BY total_pagu_pl DESC
        LIMIT 20
    """)
    
    return pd.read_sql(query, engine)

def detect_risk_score(engine):
    """Hitung risk score untuk setiap paket"""
    
    query = text("""
        WITH risk_calc AS (
            SELECT 
                r.id,
                r.nama_paket,
                r.instansi,
                r.jenis,
                r.metode,
                r.pagu,
                r.tahun,
                -- Risk factor 1: Nilai di atas 1 Miliar (30 poin)
                CASE WHEN r.pagu > 1000000000 THEN 30 ELSE 0 END as risk_nilai,
                -- Risk factor 2: Metode Pengadaan Langsung (40 poin)
                CASE WHEN r.metode = 'PENGADAAN_LANGSUNG' THEN 40 ELSE 0 END as risk_metode,
                -- Risk factor 3: Instansi dengan banyak PL (20 poin)
                CASE WHEN i.paket_pl > 10 THEN 20 ELSE 0 END as risk_instansi_pl,
                -- Risk factor 4: Instansi dengan total pagu besar (10 poin)
                CASE WHEN i.total_pagu > 50000000000 THEN 10 ELSE 0 END as risk_instansi_besar
            FROM rup_paket r
            LEFT JOIN (
                SELECT 
                    instansi,
                    COUNT(*) FILTER (WHERE metode = 'PENGADAAN_LANGSUNG') as paket_pl,
                    SUM(pagu) as total_pagu
                FROM rup_paket
                GROUP BY instansi
            ) i ON r.instansi = i.instansi
            WHERE r.pagu > 0
        )
        SELECT 
            *,
            (risk_nilai + risk_metode + risk_instansi_pl + risk_instansi_besar) as risk_score,
            CASE 
                WHEN (risk_nilai + risk_metode + risk_instansi_pl + risk_instansi_besar) >= 70 THEN 'KRITIS'
                WHEN (risk_nilai + risk_metode + risk_instansi_pl + risk_instansi_besar) >= 50 THEN 'TINGGI'
                WHEN (risk_nilai + risk_metode + risk_instansi_pl + risk_instansi_besar) >= 30 THEN 'SEDANG'
                ELSE 'RENDAH'
            END as risk_level
        FROM risk_calc
        ORDER BY risk_score DESC, pagu DESC
        LIMIT 50
    """)
    
    return pd.read_sql(query, engine)

# =========================================================
# EKSEKUSI UTAMA
# =========================================================

def main():
    print("=" * 80)
    print("ANALISIS RISIKO PENGADAAN - NEMESIS MADINA")
    print("=" * 80)
    
    engine = create_engine(DATABASE_URL)
    
    # 1. Anomali Nilai
    print("\n🔴 1. PAKET DENGAN NILAI ANOMALI (Z-Score > 3)")
    print("-" * 80)
    high_value = detect_high_value_anomalies(engine)
    if len(high_value) > 0:
        for _, row in high_value.iterrows():
            print(f"   📦 {row['nama_paket'][:60]}...")
            print(f"      Instansi: {row['instansi']} | Nilai: Rp {row['pagu']:,.0f} | Z-Score: {row['z_score']:.2f}")
            print(f"      Metode: {row['metode']} | Jenis: {row['jenis']}")
            print()
    else:
        print("   Tidak ditemukan anomali nilai")
    
    # 2. Metode Pengadaan
    print("\n🟡 2. ANALISIS METODE PENGADAAN")
    print("-" * 80)
    methods = detect_method_anomalies(engine)
    for _, row in methods.iterrows():
        print(f"   📋 {row['metode']}:")
        print(f"      Total Paket: {row['total_paket']} | Total Pagu: Rp {row['total_pagu']:,.0f}")
        print(f"      Paket > 1M: {row['paket_miliar']} | Paket > 5M: {row['paket_lima_miliar']}")
        print()
    
    # 3. Instansi Berisiko
    print("\n🟠 3. INSTANSI DENGAN POLA TIDAK BIASA")
    print("-" * 80)
    instansi = detect_instansi_anomalies(engine)
    for _, row in instansi.head(10).iterrows():
        print(f"   🏢 {row['instansi']}:")
        print(f"      Total Paket: {row['total_paket']} | Total Pagu: Rp {row['total_pagu']:,.0f}")
        print(f"      Metode Dominan: {row['metode_dominan']} ({row['paket_pl']}/{row['paket_ep']}/{row['paket_tender']})")
        print()
    
    # 4. Single Bidder Risk (Pengadaan Langsung nilai besar)
    print("\n🔴 4. RISIKO PENGADAAN LANGSUNG NILAI BESAR")
    print("-" * 80)
    single_bidder = detect_single_bidder_risk(engine)
    if len(single_bidder) > 0:
        for _, row in single_bidder.iterrows():
            print(f"   ⚠️ {row['instansi']}:")
            print(f"      Total PL: {row['total_paket_pl']} paket (Rp {row['total_pagu_pl']:,.0f})")
            print(f"      PL > 500jt: {row['paket_pl_diatas_500jt']} paket (Rp {row['total_pl_diatas_500jt']:,.0f})")
            print()
    else:
        print("   Tidak ditemukan risiko signifikan")
    
    # 5. Risk Score
    print("\n🎯 5. RISK SCORE - PAKET PRIORITAS AUDIT")
    print("-" * 80)
    risk_scores = detect_risk_score(engine)
    
    print("\n   📊 PAKET DENGAN RISIKO KRITIS & TINGGI:")
    for _, row in risk_scores.iterrows():
        if row['risk_level'] in ['KRITIS', 'TINGGI']:
            print(f"   🚨 [{row['risk_level']} - Score {row['risk_score']}] {row['nama_paket'][:50]}...")
            print(f"      Instansi: {row['instansi']} | Nilai: Rp {row['pagu']:,.0f} | Metode: {row['metode']}")
            print()
    
    # 6. Seasonal Anomalies
    print("\n📅 6. LONJAKAN PENGADAAN PER BULAN")
    print("-" * 80)
    seasonal = detect_seasonal_anomalies(engine)
    for _, row in seasonal.iterrows():
        print(f"   {int(row['tahun'])}-{int(row['bulan']):02d}: {row['total_paket']} paket | Rp {row['total_pagu']:,.0f} ({row['persentase_tahunan']:.1f}%)")
    
    # 7. Duplicate Suspicions
    print("\n🔍 7. PAKET DUPLIKAT YANG MENCURIGAKAN")
    print("-" * 80)
    duplicates = detect_duplicate_suspicions(engine)
    if len(duplicates) > 0:
        for _, row in duplicates.iterrows():
            print(f"   📦 {row['instansi']}:")
            print(f"      Paket 1: {row['paket1'][:40]}... (Rp {row['pagu1']:,.0f})")
            print(f"      Paket 2: {row['paket2'][:40]}... (Rp {row['pagu2']:,.0f})")
            print(f"      Selisih: Rp {row['selisih_pagu']:,.0f}")
            print()
    else:
        print("   Tidak ditemukan paket duplikat mencurigakan")
    
    # Simpan hasil ke Excel
    output_file = "procurement_risk_analysis.xlsx"
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        high_value.to_excel(writer, sheet_name='1_Nilai_Anomali', index=False)
        methods.to_excel(writer, sheet_name='2_Analisis_Metode', index=False)
        instansi.to_excel(writer, sheet_name='3_Instansi_Berisiko', index=False)
        single_bidder.to_excel(writer, sheet_name='4_Risiko_PL_Nilai_Besar', index=False)
        risk_scores.to_excel(writer, sheet_name='5_Risk_Score', index=False)
        seasonal.to_excel(writer, sheet_name='6_Lonjakan_Bulanan', index=False)
        duplicates.to_excel(writer, sheet_name='7_Paket_Duplikat', index=False)
    
    print("\n" + "=" * 80)
    print(f"✅ Analisis selesai! Hasil disimpan ke {output_file}")
    print("=" * 80)

if __name__ == "__main__":
    main()
