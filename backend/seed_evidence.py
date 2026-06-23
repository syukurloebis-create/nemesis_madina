#!/usr/bin/env python3
"""
Seed Evidence - Menambahkan data evidence untuk testing Phase 2
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
import random
from datetime import datetime, timedelta
from sqlalchemy import text, create_engine
from sqlalchemy.pool import NullPool

try:
    from config import settings
except ImportError:
    from config import settings

DATABASE_URL = settings.DATABASE_URL
engine = create_engine(DATABASE_URL, poolclass=NullPool)

def seed_evidence():
    print("=" * 60)
    print("🌱 SEEDING EVIDENCE DATA")
    print("=" * 60)
    
    with engine.connect() as conn:
        # 1. Get cases
        cases = conn.execute(
            text("SELECT id, title FROM cases")
        ).fetchall()
        
        print(f"Found {len(cases)} cases")
        
        evidence_types = [
            ("Dokumen Kontrak", "application/pdf", "pdf"),
            ("Bukti Transfer", "application/pdf", "pdf"),
            ("Surat Perintah", "application/pdf", "pdf"),
            ("Rekaman Wawancara", "audio/mp3", "mp3"),
            ("Screenshot", "image/png", "png"),
            ("Laporan Audit", "application/pdf", "pdf"),
            ("Data Transaksi", "application/vnd.ms-excel", "xlsx"),
            ("Email", "text/plain", "txt"),
        ]
        
        total_evidence = 0
        
        for case in cases:
            case_id = case[0]
            case_title = str(case[1])[:20] if case[1] else "Untitled"
            
            print(f"\n  Processing case: {case_title}...")
            
            # Create 3-5 evidence per case
            num_evidence = random.randint(3, 5)
            
            for i in range(num_evidence):
                evidence_id = str(uuid.uuid4())
                ev_type, mime, ext = random.choice(evidence_types)
                file_size = random.randint(100 * 1024, 10 * 1024 * 1024)
                status = random.choice(["pending", "verified", "rejected"])
                verified_at = datetime.now() - timedelta(days=random.randint(0, 30)) if status == "verified" else None
                
                # Insert evidence
                conn.execute(
                    text("""
                        INSERT INTO evidence (
                            id, case_id, filename, file_type, 
                            file_size, file_hash, status, verified_at,
                            uploaded_at, updated_at
                        ) VALUES (
                            :id, :case_id, :filename, :file_type,
                            :file_size, :file_hash, :status, :verified_at,
                            :uploaded_at, :updated_at
                        )
                    """),
                    {
                        "id": evidence_id,
                        "case_id": case_id,
                        "filename": f"evidence_{i+1}_{str(case_id)[:8]}.{ext}",
                        "file_type": mime,
                        "file_size": file_size,
                        "file_hash": f"hash_{uuid.uuid4().hex[:32]}",
                        "status": status,
                        "verified_at": verified_at,
                        "uploaded_at": datetime.now() - timedelta(days=random.randint(0, 10)),
                        "updated_at": datetime.now() - timedelta(days=random.randint(0, 5))
                    }
                )
                
                # Insert evidence file
                conn.execute(
                    text("""
                        INSERT INTO evidence_files (
                            id, evidence_id, case_id, filename,
                            sha256_hash, file_size, mime_type, uploaded_at
                        ) VALUES (
                            :id, :evidence_id, :case_id, :filename,
                            :hash, :size, :mime, :uploaded_at
                        )
                    """),
                    {
                        "id": str(uuid.uuid4()),
                        "evidence_id": evidence_id,
                        "case_id": case_id,
                        "filename": f"evidence_{i+1}_{str(case_id)[:8]}.{ext}",
                        "hash": f"sha256_{uuid.uuid4().hex[:64]}",
                        "size": file_size,
                        "mime": mime,
                        "uploaded_at": datetime.now() - timedelta(days=random.randint(0, 10))
                    }
                )
                
                total_evidence += 1
            
            conn.commit()
            print(f"    ✅ Added {num_evidence} evidence")
        
        print("\n" + "=" * 60)
        print(f"✅ EVIDENCE SEEDED! Total evidence: {total_evidence}")
        print("=" * 60)
        
        # Verifikasi
        result = conn.execute(
            text("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN status = 'verified' THEN 1 END) as verified,
                    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending,
                    COUNT(DISTINCT case_id) as cases
                FROM evidence
            """)
        ).fetchone()
        
        print(f"\n📊 Verification:")
        print(f"  Total evidence: {result[0]}")
        print(f"  Verified: {result[1]}")
        print(f"  Pending: {result[2]}")
        print(f"  Cases with evidence: {result[3]}")

if __name__ == "__main__":
    seed_evidence()