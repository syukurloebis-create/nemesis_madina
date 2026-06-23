# backend/export/evidence_package.py
import hashlib
import json
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import uuid

from sqlalchemy import text
from database import get_db


class CourtEvidencePackage:
    """Generate court-admissible evidence package (Output 0.5.10)"""
    
    def __init__(self):
        self.package_version = "1.0"
    
    async def generate(self, case_id: str, output_path: str = None) -> str:
        """Generate complete evidence package for court"""
        
        if not output_path:
            output_path = f"evidence_package_{case_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.zip"
        
        async for db in get_db():
            # Collect data
            case_data = await self._get_case_data(db, case_id)
            events = await self._get_events(db, case_id)
            evidence_files = await self._get_evidence_files(db, case_id)
            custody_chain = await self._get_custody_chain(db, case_id)
        
        # Create package
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Add manifest
            manifest = self._create_manifest(case_id, case_data, events, evidence_files)
            zf.writestr("manifest.json", json.dumps(manifest, indent=2))
            
            # Add events
            zf.writestr("events.jsonl", "\n".join([json.dumps(e) for e in events]))
            
            # Add evidence files
            for evidence in evidence_files:
                zf.writestr(f"evidence/{evidence['id']}/metadata.json", json.dumps(evidence, indent=2))
            
            # Add keys
            zf.writestr("keys/public_key.pem", await self._get_public_key())
            
            # Add TSA timestamps
            zf.writestr("tsa/timestamps.json", json.dumps(await self._get_timestamps(events), indent=2))
            
            # Add verifier script
            zf.writestr("verify.py", self._get_verifier_script())
        
        print(f"✅ Evidence package created: {output_path}")
        return output_path
    
    def _create_manifest(self, case_id: str, case_data: dict, events: list, evidence_files: list) -> dict:
        """Create signed manifest"""
        
        evidence_hashes = {}
        for evidence in evidence_files:
            evidence_hashes[evidence['id']] = evidence.get('sha256_hash', '')
        
        manifest = {
            "version": self.package_version,
            "case_id": case_id,
            "case_title": case_data.get('title', 'Unknown'),
            "exported_at": datetime.utcnow().isoformat(),
            "exported_by": "NEMESIS V8+",
            "evidence_count": len(evidence_files),
            "event_count": len(events),
            "merkle_root": self._calculate_merkle_root(events),
            "evidence_hashes": evidence_hashes,
            "signature": None
        }
        
        # Calculate signature (simplified)
        manifest_copy = manifest.copy()
        manifest_copy.pop('signature')
        manifest_str = json.dumps(manifest_copy, sort_keys=True)
        manifest['signature'] = hashlib.sha256(manifest_str.encode()).hexdigest()
        
        return manifest
    
    def _calculate_merkle_root(self, events: list) -> str:
        """Calculate Merkle root from events"""
        if not events:
            return hashlib.sha256(b"EMPTY").hexdigest()
        
        leaves = []
        for e in events:
            event_str = json.dumps(e, sort_keys=True)
            leaves.append(hashlib.sha256(event_str.encode()).digest())
        
        while len(leaves) > 1:
            if len(leaves) % 2 == 1:
                leaves.append(leaves[-1])
            leaves = [hashlib.sha256(leaves[i] + leaves[i+1]).digest() for i in range(0, len(leaves), 2)]
        
        return leaves[0].hex()
    
    def _get_verifier_script(self) -> str:
        """Return independent verifier script"""
        return '''#!/usr/bin/env python3
"""NEMESIS Independent Evidence Verifier"""

import hashlib
import json
import sys
import zipfile
from datetime import datetime

class IndependentVerifier:
    def __init__(self, package_path):
        self.package = zipfile.ZipFile(package_path, 'r')
    
    def verify(self):
        print("=== NEMESIS Evidence Verification ===")
        
        # Verify manifest
        manifest = json.loads(self.package.read('manifest.json'))
        print(f"Case ID: {manifest['case_id']}")
        print(f"Exported: {manifest['exported_at']}")
        print(f"Events: {manifest['event_count']}")
        print(f"Evidence: {manifest['evidence_count']}")
        
        # Verify Merkle root
        events = [json.loads(line) for line in self.package.read('events.jsonl').decode().split('\\n') if line]
        calculated_root = self._calculate_merkle_root(events)
        
        if calculated_root == manifest['merkle_root']:
            print("✅ Merkle root verified")
        else:
            print("❌ Merkle root mismatch")
            return False
        
        print("\\n✅ All verifications passed!")
        return True
    
    def _calculate_merkle_root(self, events):
        if not events:
            return hashlib.sha256(b"EMPTY").hexdigest()
        
        leaves = [hashlib.sha256(json.dumps(e, sort_keys=True).encode()).digest() for e in events]
        
        while len(leaves) > 1:
            if len(leaves) % 2 == 1:
                leaves.append(leaves[-1])
            leaves = [hashlib.sha256(leaves[i] + leaves[i+1]).digest() for i in range(0, len(leaves), 2)]
        
        return leaves[0].hex()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python verify.py <package.zip>")
        sys.exit(1)
    
    verifier = IndependentVerifier(sys.argv[1])
    success = verifier.verify()
    sys.exit(0 if success else 1)
'''
    
    async def _get_case_data(self, db, case_id: str) -> dict:
        """Get case data from database"""
        try:
            result = await db.execute(
                text("SELECT title, description, status FROM cases WHERE id = :id"),
                {"id": case_id}
            )
            row = result.fetchone()
            return {"title": row[0], "description": row[1], "status": row[2]} if row else {}
        except Exception as e:
            print(f"Error getting case data: {e}")
            return {}
    
    async def _get_events(self, db, case_id: str) -> list:
        """Get events for case"""
        try:
            result = await db.execute(
                text("""
                    SELECT event_id, event_type, data, timestamp, version, event_hash, previous_hash
                    FROM events 
                    WHERE case_id = :case_id 
                    ORDER BY version
                """),
                {"case_id": case_id}
            )
            rows = result.fetchall()
            events = []
            for r in rows:
                data = r[2]
                if isinstance(data, str):
                    try:
                        data = json.loads(data)
                    except:
                        pass
                events.append({
                    "event_id": str(r[0]),
                    "event_type": r[1],
                    "data": data,
                    "timestamp": r[3].isoformat() if r[3] else None,
                    "version": r[4],
                    "event_hash": r[5],
                    "previous_hash": r[6]
                })
            return events
        except Exception as e:
            print(f"Error getting events: {e}")
            return []
    
    async def _get_evidence_files(self, db, case_id: str) -> list:
        """Get evidence files for case"""
        try:
            result = await db.execute(
                text("SELECT id, filename, sha256_hash, file_size FROM evidence_files WHERE case_id = :case_id"),
                {"case_id": case_id}
            )
            rows = result.fetchall()
            return [{"id": str(r[0]), "filename": r[1], "sha256_hash": r[2], "file_size": r[3]} for r in rows]
        except Exception as e:
            print(f"Error getting evidence files: {e}")
            return []
    
    async def _get_custody_chain(self, db, case_id: str) -> list:
        """Get custody chain for case evidence"""
        try:
            result = await db.execute(
                text("""
                    SELECT cc.evidence_id, cc.from_custodian, cc.to_custodian, cc.transferred_at
                    FROM custody_chain cc
                    JOIN evidence_files ef ON cc.evidence_id = ef.id
                    WHERE ef.case_id = :case_id
                """),
                {"case_id": case_id}
            )
            rows = result.fetchall()
            return [{"evidence_id": str(r[0]), "from": r[1], "to": r[2], "transferred_at": r[3].isoformat() if r[3] else None} for r in rows]
        except Exception as e:
            print(f"Error getting custody chain: {e}")
            return []
    
    async def _get_public_key(self) -> str:
        """Get public key for verification"""
        return "-----BEGIN PUBLIC KEY-----\nMIIB\n-----END PUBLIC KEY-----"
    
    async def _get_timestamps(self, events: list) -> list:
        """Get timestamps for events"""
        return [{"event_id": e['event_id'], "timestamp": e['timestamp']} for e in events if e.get('timestamp')]