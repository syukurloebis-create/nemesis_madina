# scripts/tests/golden/generate_golden.py
"""
Generate golden dataset from official baseline.
"""

import json
import asyncio
from pathlib import Path

from metadata_inventory.phase2_runner import Phase2Runner
from metadata_inventory.phase3_runner import Phase3Runner


def generate_golden():
    """Generate golden dataset from official baseline."""
    print("\n" + "="*80)
    print(" GENERATING GOLDEN DATASET")
    print("="*80 + "\n")
    
    # Run Phase 2 to generate discovery artifact
    print("Running Phase 2 Discovery...")
    runner2 = Phase2Runner()
    result2 = asyncio.run(runner2.run())
    
    # Extract discovery artifact
    discovery_result = result2.get("results", {}).get("discovery_artifact", {})
    if discovery_result.get("status") == "COMPLETED":
        golden_dir = Path("scripts/tests/golden/golden_data")
        golden_dir.mkdir(parents=True, exist_ok=True)
        
        # Save discovery artifact
        artifact_path = golden_dir / "discovery_artifact.json"
        
        # Get artifact from runner (simplified)
        artifact_data = {
            "fingerprint": discovery_result.get("fingerprint", ""),
            "checksum": discovery_result.get("checksum", ""),
            "timestamp": "2026-08-05T12:00:00.000000",  # Normalized for golden
            "registry_count": discovery_result.get("registry_count", 0),
            "model_count": discovery_result.get("model_count", 0),
            "mapper_count": discovery_result.get("mapper_count", 0)
        }
        
        with open(artifact_path, "w") as f:
            json.dump(artifact_data, f, indent=2)
        
        print(f"  ✅ Golden discovery artifact saved: {artifact_path}")
    
    # Run Phase 3 to generate verification result
    print("Running Phase 3 Verification...")
    runner3 = Phase3Runner()
    result3 = asyncio.run(runner3.run())
    
    report_result = result3.get("results", {}).get("report", {})
    if report_result.get("status") == "COMPLETED":
        verification_path = golden_dir / "verification_result.json"
        
        # Save verification result
        verification_data = {
            "status": report_result.get("status", "UNKNOWN"),
            "finding_count": report_result.get("finding_count", 0),
            "timestamp": "2026-08-05T12:00:00.000000"  # Normalized
        }
        
        with open(verification_path, "w") as f:
            json.dump(verification_data, f, indent=2)
        
        print(f"  ✅ Golden verification result saved: {verification_path}")
    
    print("\n" + "="*80)
    print(" GOLDEN DATASET GENERATED")
    print("="*80 + "\n")


if __name__ == "__main__":
    generate_golden()