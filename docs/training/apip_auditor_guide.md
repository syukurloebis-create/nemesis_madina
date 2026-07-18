# NEMESIS V8.1 - APIP Auditor Training Guide

## Introduction

NEMESIS V8.1 adalah Strategic Intelligence Center untuk APIP yang membantu auditor dalam:

1. **Fraud Detection** - Mendeteksi indikasi fraud
2. **Risk Assessment** - Menilai risiko secara komprehensif
3. **Decision Support** - Memberikan rekomendasi berbasis data
4. **Graph Intelligence** - Melihat relasi antar entitas
5. **Predictive Analytics** - Memprediksi risiko di masa depan

## Getting Started

### Login

1. Buka `http://localhost:8000/auth/login`
2. Masukkan username dan password
3. Dashboard utama akan muncul

### Dashboard Overview

Dashboard utama menampilkan:

- **KPI Cards**: Total Cases, Fraud Detection, Risk Score, Graph Metrics
- **Risk Chart**: Distribusi risiko per kasus
- **Alert Center**: Notifikasi real-time
- **Recent Cases**: Kasus terbaru yang perlu ditindaklanjuti

## Key Features

### 1. Risk Assessment

**Cara Menggunakan:**

1. Klik menu "Risk Assessment"
2. Pilih case yang akan dianalisis
3. Lihat risk score dan faktor-faktor yang mempengaruhinya
4. Klik "Explain" untuk melihat detail penjelasan

**Interpretasi Risk Score:**

| Score | Level | Action |
|-------|-------|--------|
| 0-30 | LOW | Monitoring rutin |
| 30-60 | MEDIUM | Perlu investigasi lanjutan |
| 60-80 | HIGH | Segera audit |
| 80-100 | CRITICAL | Tindakan darurat |

### 2. Fraud Detection

**Cara Menggunakan:**

1. Klik menu "Fraud Detection"
2. Sistem akan menampilkan fraud probability
3. Lihat faktor-faktor yang berkontribusi
4. Ekspor laporan jika diperlukan

### 3. Graph Intelligence

**Cara Menggunakan:**

1. Klik menu "Graph Intelligence"
2. Pilih case atau entity
3. Lihat visualisasi relasi
4. Deteksi collusion patterns

### 4. Recommendation Center

**Cara Menggunakan:**

1. Klik menu "Recommendations"
2. Lihat rekomendasi yang dihasilkan AI
3. Prioritaskan berdasarkan urgency
4. Implementasikan rekomendasi

### 5. Decision Support

**Cara Menggunakan:**

1. Klik menu "Decisions"
2. Buat keputusan baru
3. Pilih opsi yang tersedia
4. Track impact dari keputusan

## Reporting

### Generate Report

1. Klik menu "Reports"
2. Pilih tipe report (Risk, Fraud, Graph)
3. Tentukan periode waktu
4. Klik "Generate"
5. Download dalam format PDF/Excel

## Troubleshooting

### Common Issues

**Issue**: Cannot login
**Solution**: Reset password via "Forgot Password"

**Issue**: Dashboard not loading
**Solution**: Refresh browser or clear cache

**Issue**: Data not updating
**Solution**: Click refresh button or restart browser

## Support

- **Email**: support@nemesis.local
- **Documentation**: http://localhost:8000/docs
- **Training Schedule**: Weekly every Friday 10:00 AM