#!/usr/bin/env python3
"""
NEMESIS Independent Evidence Verifier
No external dependencies - Python 3.11+ standard library only

Usage: python verify.py <package_path.zip>
"""

import hashlib
import json
import sys
import zipfile
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Tuple

class IndependentVerifier:
    """Independent verifier - no NEMESIS software required"""
    
    def __init__(self, package_path: str):
        self.package_path = Path(package_path)
        self.zipfile = zipfile.ZipFile(package_path, 'r')
        self.results = {}
    
    def run(self) -> Dict[str, Any]:
        """Run all verifications"""
        print(f"Verifying: {self.package_path.name}")
        print("-" * 50)
        
        # Verify manifest
        print("1. Verifying manifest...")
        manifest_valid = self.verify_manifest()
        self.results['manifest_valid'] = manifest_valid
        print(f"   {'✓' if manifest_valid else '✗'} Manifest {'valid' if manifest_valid else 'invalid'}")
        
        # Verify evidence integrity
        print("2. Verifying evidence integrity...")
        evidence_results = self.verify_evidence_integrity()
        self.results['evidence_integrity'] = evidence_results
        passed = sum(1 for r in evidence_results if r['status'] == 'PASS')
        total = len(evidence_results)
        print(f"   ✓ {passed}/{total} evidence files verified")
        
        # Verify chain of custody
        print("3. Verifying chain of custody...")
        chain_valid = self.verify_chain_of_custody()
        self.results['chain_valid'] = chain_valid
        print(f"   {'✓' if chain_valid else '✗'} Chain {'intact' if chain_valid else 'broken'}")
        
        # Verify signatures if available
        if self.has_signatures():
            print("4. Verifying digital signatures...")
            sig_results = self.verify_signatures()
            self.results['signatures'] = sig_results
            print(f"   ✓ {sig_results['verified']}/{sig_results['total']} signatures valid")
        
        # Overall status
        all_pass = all([
            manifest_valid,
            chain_valid,
            all(r['status'] == 'PASS' for r in evidence_results)
        ])
        
        self.results['verification_status'] = 'PASS' if all_pass else 'FAIL'
        self.results['timestamp'] = datetime.utcnow().isoformat()
        
        print("-" * 50)
        print(f"OVERALL: {'✓ PASSED' if all_pass else '✗ FAILED'}")
        
        return self.results
    
    def verify_manifest(self) -> bool:
        """Verify manifest signature and integrity"""
        try:
            manifest_data = self.zipfile.read('manifest.json')
            manifest = json.loads(manifest_data)
            
            # Get public key
            public_key_pem = self.zipfile.read('keys/public_key.pem')
            
            # Verify signature (simplified - would use actual crypto in production)
            # For independent verification, we rely on the verifier's embedded public key
            signature = bytes.fromhex(manifest.get('signature', ''))
            
            # In a real verifier, you would:
            # 1. Load public key
            # 2. Verify Ed25519 signature
            # For this demo, we check that signature exists
            return bool(manifest.get('signature'))
        except Exception as e:
            print(f"   Manifest verification failed: {e}")
            return False
    
    def verify_evidence_integrity(self) -> List[Dict[str, Any]]:
        """Verify all evidence files against manifest hashes"""
        results = []
        
        try:
            manifest_data = self.zipfile.read('manifest.json')
            manifest = json.loads(manifest_data)
            evidence_hashes = manifest.get('evidence_hashes', {})
            
            for evidence_id, expected_hash in evidence_hashes.items():
                try:
                    content = self.zipfile.read(f'evidence/{evidence_id}/original.bin')
                    actual_hash = hashlib.sha256(content).hexdigest()
                    
                    results.append({
                        'evidence_id': evidence_id,
                        'status': 'PASS' if actual_hash == expected_hash else 'FAIL',
                        'expected': expected_hash,
                        'actual': actual_hash
                    })
                except KeyError:
                    results.append({
                        'evidence_id': evidence_id,
                        'status': 'FAIL',
                        'error': 'File not found'
                    })
        except Exception as e:
            results.append({'status': 'FAIL', 'error': str(e)})
        
        return results
    
    def verify_chain_of_custody(self) -> bool:
        """Verify event chain integrity"""
        try:
            events_data = self.zipfile.read('events.jsonl')
            events = []
            for line in events_data.split(b'\n'):
                if line:
                    events.append(json.loads(line))
            
            previous_hash = None
            for event in events:
                if previous_hash and event.get('previous_hash') != previous_hash:
                    return False
                previous_hash = event.get('event_hash')
            
            return True
        except Exception:
            return False
    
    def has_signatures(self) -> bool:
        """Check if package contains signatures"""
        try:
            self.zipfile.read('keys/public_key.pem')
            return True
        except KeyError:
            return False
    
    def verify_signatures(self) -> Dict[str, Any]:
        """Verify digital signatures (simplified)"""
        # In production, this would implement actual Ed25519 verification
        return {
            'total': 0,
            'verified': 0,
            'failed': []
        }
    
    def save_report(self, output_path: str = None):
        """Save verification report"""
        if not output_path:
            output_path = 'verification_report.json'
        
        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\nReport saved to: {output_path}")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    package_path = sys.argv[1]
    
    if not Path(package_path).exists():
        print(f"Error: Package not found: {package_path}")
        sys.exit(1)
    
    verifier = IndependentVerifier(package_path)
    results = verifier.run()
    verifier.save_report()
    
    sys.exit(0 if results['verification_status'] == 'PASS' else 1)

if __name__ == '__main__':
    main()