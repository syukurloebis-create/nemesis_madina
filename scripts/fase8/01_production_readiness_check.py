#!/usr/bin/env python3
"""
NEMESIS FASE 8 - Production Readiness Check
"""

import sys
import os
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Tuple

SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

REPORT_DIR = PROJECT_ROOT / "reports" / "fase8"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

# Simple logging functions
def log_success(msg):
    print(f"  ✅ {msg}")

def log_warning(msg):
    print(f"  ⚠️ {msg}")

def log_error(msg):
    print(f"  ❌ {msg}")

class ProductionReadinessChecker:
    """Check if system is ready for production"""
    
    def __init__(self):
        self.results: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "checks": {},
            "overall_status": "pending"
        }
        self.score = 0
        self.max_score = 0
    
    def check_architecture(self) -> Tuple[bool, str, int]:
        """Check architecture compliance"""
        print("\n  Checking architecture...")
        
        issues = []
        score = 0
        max_score = 10
        
        # Check for canonical structure
        required_dirs = [
            "backend/evidence",
            "backend/websocket", 
            "backend/graph",
            "backend/lineage",
            "backend/schema"
        ]
        
        for dir_name in required_dirs:
            if (PROJECT_ROOT / dir_name).exists():
                score += 2
                print(f"    ✅ {dir_name} exists")
            else:
                issues.append(f"Missing directory: {dir_name}")
        
        passed = len(issues) == 0
        return passed, "; ".join(issues) if issues else "All architecture checks passed", score
    
    def check_runtime(self) -> Tuple[bool, str, int]:
        """Check runtime health"""
        print("\n  Checking runtime...")
        
        issues = []
        score = 0
        max_score = 10
        
        # Check if server is running
        import requests
        try:
            resp = requests.get("http://localhost:8000/health", timeout=5)
            if resp.status_code == 200:
                score += 5
                print("    ✅ Server is running")
            else:
                issues.append(f"Server returned {resp.status_code}")
        except:
            issues.append("Server not running")
        
        # Check health endpoints
        endpoints = ["/health", "/health/live", "/health/ready", "/metrics"]
        for endpoint in endpoints:
            try:
                resp = requests.get(f"http://localhost:8000{endpoint}", timeout=5)
                if resp.status_code == 200:
                    score += 1
                    print(f"    ✅ {endpoint} OK")
                else:
                    issues.append(f"{endpoint} returned {resp.status_code}")
            except:
                issues.append(f"{endpoint} not accessible")
        
        passed = len(issues) == 0
        return passed, "; ".join(issues) if issues else "All runtime checks passed", score
    
    def check_data_integrity(self) -> Tuple[bool, str, int]:
        """Check data integrity"""
        print("\n  Checking data integrity...")
        
        issues = []
        score = 0
        max_score = 10
        
        try:
            from backend.evidence import EvidenceRegistry, EvidenceHasher
            
            registry = EvidenceRegistry()
            hasher = EvidenceHasher()
            
            # Test hash consistency
            test_data = {"test": "integrity_check"}
            hash1 = hasher.compute_hash(test_data)
            hash2 = hasher.compute_hash(test_data)
            
            if hash1 == hash2:
                score += 3
                print("    ✅ Hash consistency OK")
            else:
                issues.append("Hash inconsistency")
            
            # Test evidence creation
            evidence = registry.create(test_data, "readiness_test")
            if evidence and evidence.id:
                score += 3
                print(f"    ✅ Evidence creation OK")
            else:
                issues.append("Evidence creation failed")
            
            # Test verification
            if registry.verify(evidence.id):
                score += 2
                print("    ✅ Evidence verification OK")
            else:
                issues.append("Evidence verification failed")
            
        except Exception as e:
            issues.append(f"Data integrity error: {e}")
        
        passed = len(issues) == 0
        return passed, "; ".join(issues) if issues else "All data integrity checks passed", score
    
    def check_intelligence(self) -> Tuple[bool, str, int]:
        """Check intelligence/ML components"""
        print("\n  Checking intelligence components...")
        
        issues = []
        score = 0
        max_score = 10
        
        try:
            from backend.intelligence.ml.anomaly import AnomalyDetector
            from backend.intelligence.ml.scoring import RiskScorer
            
            detector = AnomalyDetector()
            scorer = RiskScorer()
            
            # Test anomaly detection
            data = [1, 2, 3, 100, 4, 5, 6]
            anomalies = detector.detect(data)
            if anomalies:
                score += 3
                print("    ✅ Anomaly detection OK")
            else:
                issues.append("Anomaly detection failed")
            
            # Test risk scoring
            score_val = scorer.compute_score({"anomaly_score": 0.8})
            if 0 <= score_val <= 1:
                score += 3
                print(f"    ✅ Risk scoring OK")
            else:
                issues.append("Risk scoring failed")
            
            # Test calibration
            from backend.intelligence.ml.calibration import ConfidenceCalibrator
            calibrator = ConfidenceCalibrator()
            calibrated = calibrator.calibrate(0.8)
            if 0 <= calibrated <= 1:
                score += 2
                print("    ✅ Calibration OK")
                
        except Exception as e:
            issues.append(f"Intelligence error: {e}")
        
        passed = len(issues) == 0
        return passed, "; ".join(issues) if issues else "All intelligence checks passed", score
    
    def check_observability(self) -> Tuple[bool, str, int]:
        """Check observability components"""
        print("\n  Checking observability...")
        
        issues = []
        score = 0
        max_score = 10
        
        try:
            from backend.telemetry.metrics import metrics_registry
            
            # Test metrics
            metrics_registry.counter("test_metric", 1)
            metrics = metrics_registry.get_all_metrics()
            if "test_metric" in metrics:
                score += 5
                print("    ✅ Metrics OK")
            else:
                issues.append("Metrics registration failed")
            
            # Test health endpoints via API
            import requests
            resp = requests.get("http://localhost:8000/metrics", timeout=5)
            if resp.status_code == 200:
                score += 5
                print("    ✅ Metrics endpoint accessible")
                
        except Exception as e:
            issues.append(f"Observability error: {e}")
        
        passed = len(issues) == 0
        return passed, "; ".join(issues) if issues else "All observability checks passed", score
    
    def run_all(self) -> Dict[str, Any]:
        """Run all checks"""
        print("\n" + "="*60)
        print("PRODUCTION READINESS CHECK")
        print("="*60)
        
        checks = [
            ("Architecture", self.check_architecture),
            ("Runtime", self.check_runtime),
            ("Data Integrity", self.check_data_integrity),
            ("Intelligence", self.check_intelligence),
            ("Observability", self.check_observability),
        ]
        
        total_score = 0
        total_max = 0
        
        for name, check_func in checks:
            print(f"\n[{name}]")
            passed, message, score = check_func()
            total_score += score
            total_max += 10
            self.results["checks"][name] = {
                "passed": passed,
                "message": message,
                "score": score,
                "max_score": 10
            }
            if passed:
                log_success(f"{name}: PASSED ({score}/10)")
            else:
                log_warning(f"{name}: PARTIAL ({score}/10) - {message[:50]}")
        
        # Calculate overall score
        percentage = (total_score / total_max) * 100 if total_max > 0 else 0
        self.results["overall_score"] = round(percentage, 1)
        self.results["overall_status"] = "READY" if percentage >= 70 else "NOT_READY"
        
        # Summary
        print("\n" + "="*60)
        print("READINESS SUMMARY")
        print("="*60)
        print(f"  Overall Score: {percentage:.1f}%")
        print(f"  Status: {self.results['overall_status']}")
        
        if percentage >= 70:
            log_success("System is ready for production!")
        elif percentage >= 50:
            log_warning("System needs improvements before production")
        else:
            log_error("System not ready for production")
        
        # Save report
        report_path = REPORT_DIR / "readiness_report.json"
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"\n  Report saved: {report_path}")
        
        return self.results


def main():
    checker = ProductionReadinessChecker()
    results = checker.run_all()
    return 0 if results["overall_score"] >= 50 else 1


if __name__ == "__main__":
    sys.exit(main())
