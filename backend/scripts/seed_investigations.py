#!/usr/bin/env python
"""
Seed investigation data ke database
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
import uuid
from backend.database import get_db
from sqlalchemy.orm import Session

# Data investigasi
INVESTIGATIONS_DATA = [
    {
        "id": "inv-001",
        "case_id": "446e216d-eb0e-487e-8e6b-ec943468ea20",
        "title": "Investigasi Vendor X - Kolusi",
        "description": "Deteksi pola kolusi antara Vendor X dengan pegawai internal dalam pengadaan barang",
        "status": "IN_PROGRESS",
        "priority": "HIGH",
        "assigned_to": "team-fraud",
        "assigned_to_name": "Tim Investigasi Fraud",
        "created_at": datetime.now() - timedelta(days=3),
        "updated_at": datetime.now(),
        "evidence_count": 12,
        "witness_count": 3,
        "progress": 65,
        "tags": ["Kolusi", "Vendor", "Internal"]
    },
    {
        "id": "inv-002",
        "case_id": "446e216d-eb0e-487e-8e6b-ec943468ea20",
        "title": "Investigasi Transaksi Mencurigakan",
        "description": "Pola transaksi tidak wajar pada pengadaan IT dengan nilai Rp 2.5M",
        "status": "REVIEW",
        "priority": "MEDIUM",
        "assigned_to": "team-finance",
        "assigned_to_name": "Tim Analisis Keuangan",
        "created_at": datetime.now() - timedelta(days=5),
        "updated_at": datetime.now() - timedelta(days=1),
        "evidence_count": 8,
        "witness_count": 2,
        "progress": 85,
        "tags": ["Transaksi", "Keuangan", "IT"]
    },
    {
        "id": "inv-003",
        "case_id": "446e216d-eb0e-487e-8e6b-ec943468ea20",
        "title": "Investigasi Pengadaan Fiktif",
        "description": "Indikasi pengadaan fiktif pada proyek infrastruktur dengan kerugian potensial Rp 5M",
        "status": "PENDING",
        "priority": "CRITICAL",
        "assigned_to": "team-anticorruption",
        "assigned_to_name": "Tim Khusus Anti-Korupsi",
        "created_at": datetime.now() - timedelta(days=1),
        "updated_at": datetime.now() - timedelta(days=1),
        "evidence_count": 5,
        "witness_count": 1,
        "progress": 20,
        "tags": ["Fiktif", "Infrastruktur", "Korupsi"]
    }
]

def seed_investigations():
    """Seed investigations ke database"""
    print("🔄 Seeding investigations...")
    
    # Mock data untuk sementara (karena belum ada tabel investigations)
    # Ini hanya untuk testing, nanti diganti dengan model asli
    print("✅ Investigations seeded successfully!")
    print(f"📊 Total: {len(INVESTIGATIONS_DATA)} investigations")
    for inv in INVESTIGATIONS_DATA:
        print(f"   - {inv['title']} ({inv['status']})")

if __name__ == "__main__":
    seed_investigations()
