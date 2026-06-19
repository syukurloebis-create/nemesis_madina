#!/usr/bin/env python3
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
        events = [json.loads(line) for line in self.package.read('events.jsonl').decode().split('\n') if line]
        calculated_root = self._calculate_merkle_root(events)
        
        if calculated_root == manifest['merkle_root']:
            print("✅ Merkle root verified")
        else:
            print("❌ Merkle root mismatch")
            return False
        
        print("\n✅ All verifications passed!")
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
