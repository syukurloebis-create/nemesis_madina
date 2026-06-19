#!/usr/bin/env python3
"""
NEMESIS FASE 8 - Final Validation (Simple)
"""

import sys
import json
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

REPORT_DIR = PROJECT_ROOT / "reports" / "fase8"
REPORT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    print("\n" + "="*60)
    print("FINAL VALIDATION")
    print("="*60)
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "status": "PASSED",
        "checks": {}
    }
    
    # Check server
    print("\n[1] Checking server...")
    try:
        import requests
        resp = requests.get("http://localhost:8000/health", timeout=5)
        if resp.status_code == 200:
            print("  [OK] Server is running")
            results["checks"]["server"] = True
        else:
            print("  [FAIL] Server returned", resp.status_code)
            results["checks"]["server"] = False
            results["status"] = "FAILED"
    except Exception as e:
        print(f"  [FAIL] Server not responding: {e}")
        results["checks"]["server"] = False
        results["status"] = "FAILED"
    
    # Check files
    print("\n[2] Checking required files...")
    required_files = [
        "README.md",
        "scripts/start_server.sh",
        "scripts/stop_server.sh",
        "scripts/monitor.sh",
        "Dockerfile",
        "docker-compose.yml"
    ]
    
    for f in required_files:
        if (PROJECT_ROOT / f).exists():
            print(f"  [OK] {f}")
            results["checks"][f] = True
        else:
            print(f"  [WARN] {f} missing")
            results["checks"][f] = False
    
    # Check reports
    print("\n[3] Checking reports...")
    report_files = [
        "readiness_report.json",
        "security_audit.json",
        "api_documentation.md"
    ]
    
    for f in report_files:
        if (REPORT_DIR / f).exists():
            print(f"  [OK] reports/{f}")
        else:
            print(f"  [WARN] reports/{f} missing")
    
    # Save final report
    final_path = REPORT_DIR / "final_validation.json"
    with open(final_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print("\n" + "="*60)
    if results["status"] == "PASSED":
        print("[OK] FINAL VALIDATION PASSED - NEMESIS IS READY!")
    else:
        print("[WARN] FINAL VALIDATION HAS WARNINGS - Check above")
    print("="*60)
    
    return 0 if results["status"] == "PASSED" else 1


if __name__ == "__main__":
    sys.exit(main())
