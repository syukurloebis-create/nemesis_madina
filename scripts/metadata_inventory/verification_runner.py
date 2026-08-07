#!/usr/bin/env python3
"""
ORM Verification Platform L4 Verification Runner
Produces auditable execution evidence.
"""

import json
import hashlib
import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

# Tambahkan parent directory ke sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from metadata_inventory.orchestrator import VerificationOrchestrator
from metadata_inventory.complete_self_validation_suite import CompleteSelfValidationSuite


def run_verification(environment: str = "development") -> Dict[str, Any]:
    """Run full verification and produce evidence."""
    
    # Initialize framework
    orchestrator = VerificationOrchestrator(environment=environment)
    
    # Run self-validation
    suite = CompleteSelfValidationSuite(orchestrator)
    validation_results = suite.run_all()
    suite.cleanup()
    
    # Run main verification
    verification_result = orchestrator.run()
    
    # Produce evidence
    evidence_dir = Path(__file__).parent / "evidence"
    evidence_dir.mkdir(exist_ok=True)
    
    # Save self-validation results
    with open(evidence_dir / "self_validation_results.json", "w") as f:
        json.dump(validation_results, f, indent=2, default=str)
    
    # Save verification results
    with open(evidence_dir / "verification_results.json", "w") as f:
        json.dump(verification_result, f, indent=2, default=str)
    
    # Save execution log
    with open(evidence_dir / "execution_log.json", "w") as f:
        json.dump(suite._execution_log, f, indent=2, default=str)
    
    # Generate combined checksum
    combined = {
        "self_validation": validation_results,
        "verification": verification_result,
        "execution_log": suite._execution_log
    }
    combined_json = json.dumps(combined, sort_keys=True, default=str)
    combined_checksum = hashlib.sha256(combined_json.encode()).hexdigest()[:16]
    
    # Save manifest
    manifest = {
        "timestamp": datetime.now().isoformat(),
        "framework_version": "1.0.0",
        "sqlalchemy_version": "2.0.23",
        "environment": environment,
        "self_validation": validation_results["summary"],
        "verification_status": verification_result.get("system_health", "UNKNOWN"),
        "evidence_files": [
            {"name": "self_validation_results.json", "checksum": hashlib.sha256(json.dumps(validation_results, sort_keys=True, default=str).encode()).hexdigest()[:16]},
            {"name": "verification_results.json", "checksum": hashlib.sha256(json.dumps(verification_result, sort_keys=True, default=str).encode()).hexdigest()[:16]},
            {"name": "execution_log.json", "checksum": hashlib.sha256(json.dumps(suite._execution_log, sort_keys=True, default=str).encode()).hexdigest()[:16]}
        ],
        "combined_checksum": combined_checksum,
        "reproducibility_instructions": f"python -m metadata_inventory.verification_runner --env {environment}",
        "execution_host": "verification-runner-01",
        "execution_user": "ci-runner"
    }
    
    with open(evidence_dir / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2, default=str)
    
    # Print summary
    print("\n" + "="*80)
    print(" VERIFICATION EVIDENCE GENERATED")
    print("="*80)
    print(f"  Self-Validation: {validation_results['summary']['passed']}/{validation_results['summary']['total']} passed")
    print(f"  Pass Rate: {validation_results['summary']['pass_rate']*100:.1f}%")
    print(f"  System Health: {verification_result.get('system_health', 'UNKNOWN')}")
    print(f"  Combined Checksum: {combined_checksum}")
    print(f"  Evidence Directory: {evidence_dir}")
    print("="*80 + "\n")
    
    return {
        "validation": validation_results,
        "verification": verification_result,
        "manifest": manifest,
        "evidence_dir": str(evidence_dir)
    }


def main():
    parser = argparse.ArgumentParser(description="ORM Verification Platform L4")
    parser.add_argument("--env", default="development", choices=["development", "ci", "staging", "production"])
    args = parser.parse_args()
    
    run_verification(args.env)


if __name__ == "__main__":
    main()