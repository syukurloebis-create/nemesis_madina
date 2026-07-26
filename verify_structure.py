#!/usr/bin/env python3
"""
verify_structure.py - Skrip untuk memeriksa struktur proyek NEMESIS Madina
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any, Optional
import json
from datetime import datetime


class StructureVerifier:
    """Verifikasi struktur proyek NEMESIS Madina"""
    
    def __init__(self, root_path: str = "."):
        self.root = Path(root_path).resolve()
        self.backend = self.root / "backend"
        self.frontend = self.root / "frontend"
        
        # Target struktur yang diharapkan
        self.expected_backend = {
            "routers": [
                "dashboard_intelligence.py",  # Target baru
                "dashboard.py",
                "graph.py",
                "fraud.py",
                "risk.py",
                "procurement.py",
                "recovery.py",
                "auth.py",
                "cases.py",
                "health.py",
            ],
            "services": [
                "dashboard_intelligence_service.py",  # Target baru
                "dashboard_snapshot_cache_manager.py",
                "dashboard_snapshot_builder.py",
                "dashboard_snapshot.py",
                "fraud_service.py",
                "graph_service.py",
                "risk_service.py",
                "procurement_service.py",
                "recovery_service.py",
                "ai_recommendation_service.py",  # Target baru
            ],
            "collectors": [  # Target baru - folder
                "__init__.py",
                "base_collector.py",
                "fraud_collector.py",
                "graph_collector.py",
                "risk_collector.py",
                "procurement_collector.py",
                "recovery_collector.py",
                "recommendation_collector.py",
            ],
            "websocket": [
                "recovery.py",
                "alert_engine.py",
            ],
            "core": [
                "config.py",
                "database.py",
                "logging.py",
            ],
            "models": [
                "case.py",
                "fraud.py",
                "graph.py",
                "risk.py",
                "procurement.py",
                "vendor.py",
            ]
        }
        
        self.expected_frontend = {
            "hooks": [
                "useIntelligenceDashboard.ts",
                "useDashboardData.tsx",
                "useRecoveryWebSocket.ts",  # Target baru
                "useFraudDetection.ts",
                "useGraphAnalysis.ts",
                "useRiskAssessment.ts",
            ],
            "services": [
                "dashboardIntelligenceApi.ts",
                "api.ts",
                "authApi.ts",
                "caseApi.ts",
                "fraudApi.ts",
                "graphApi.ts",
                "riskApi.ts",
            ],
            "components": [
                "DashboardIntelligence.tsx",
                "RecoveryIntelligence.tsx",
                "FraudAnalysis.tsx",
                "GraphVisualization.tsx",
                "RiskAssessment.tsx",
            ]
        }
    
    def check_path(self, path: Path) -> bool:
        """Cek apakah path ada"""
        return path.exists()
    
    def list_files(self, directory: Path, pattern: str = "*.py") -> List[str]:
        """List file dalam directory"""
        if not directory.exists():
            return []
        return [f.name for f in directory.glob(pattern) if f.is_file()]
    
    def check_structure(self) -> Dict[str, Any]:
        """Periksa struktur proyek"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "root": str(self.root),
            "backend": {
                "exists": self.check_path(self.backend),
                "status": "✅" if self.check_path(self.backend) else "❌",
                "routers": {},
                "services": {},
                "collectors": {},
                "websocket": {},
                "core": {},
                "models": {},
            },
            "frontend": {
                "exists": self.check_path(self.frontend),
                "status": "✅" if self.check_path(self.frontend) else "❌",
                "hooks": {},
                "services": {},
                "components": {},
            },
            "summary": {
                "total_expected": 0,
                "total_found": 0,
                "missing": [],
                "extra": [],
            }
        }
        
        # Cek Backend Routers
        routers_path = self.backend / "routers"
        if routers_path.exists():
            existing = self.list_files(routers_path)
            for expected in self.expected_backend["routers"]:
                found = expected in existing
                results["backend"]["routers"][expected] = "✅" if found else "❌"
                if not found:
                    results["summary"]["missing"].append(f"backend/routers/{expected}")
        
        # Cek Backend Services
        services_path = self.backend / "services"
        if services_path.exists():
            existing = self.list_files(services_path)
            for expected in self.expected_backend["services"]:
                found = expected in existing
                results["backend"]["services"][expected] = "✅" if found else "❌"
                if not found:
                    results["summary"]["missing"].append(f"backend/services/{expected}")
        
        # Cek Backend Collectors (folder baru)
        collectors_path = self.backend / "collectors"
        if collectors_path.exists():
            existing = self.list_files(collectors_path)
            for expected in self.expected_backend["collectors"]:
                found = expected in existing
                results["backend"]["collectors"][expected] = "✅" if found else "❌"
                if not found:
                    results["summary"]["missing"].append(f"backend/collectors/{expected}")
        else:
            for expected in self.expected_backend["collectors"]:
                results["backend"]["collectors"][expected] = "❌ (folder tidak ada)"
                results["summary"]["missing"].append(f"backend/collectors/{expected}")
        
        # Cek Backend WebSocket
        websocket_path = self.backend / "websocket"
        if websocket_path.exists():
            existing = self.list_files(websocket_path)
            for expected in self.expected_backend["websocket"]:
                found = expected in existing
                results["backend"]["websocket"][expected] = "✅" if found else "❌"
                if not found:
                    results["summary"]["missing"].append(f"backend/websocket/{expected}")
        
        # Cek Backend Core
        core_path = self.backend / "core"
        if core_path.exists():
            existing = self.list_files(core_path)
            for expected in self.expected_backend["core"]:
                found = expected in existing
                results["backend"]["core"][expected] = "✅" if found else "❌"
        
        # Cek Backend Models
        models_path = self.backend / "models"
        if models_path.exists():
            existing = self.list_files(models_path)
            for expected in self.expected_backend["models"]:
                found = expected in existing
                results["backend"]["models"][expected] = "✅" if found else "❌"
        
        # Cek Frontend Hooks
        hooks_path = self.frontend / "src" / "hooks"
        if hooks_path.exists():
            existing = [f.name for f in hooks_path.glob("*.ts*")]
            for expected in self.expected_frontend["hooks"]:
                found = expected in existing
                results["frontend"]["hooks"][expected] = "✅" if found else "❌"
                if not found:
                    results["summary"]["missing"].append(f"frontend/src/hooks/{expected}")
        
        # Cek Frontend Services
        services_path_fe = self.frontend / "src" / "services"
        if services_path_fe.exists():
            existing = [f.name for f in services_path_fe.glob("*.ts*")]
            for expected in self.expected_frontend["services"]:
                found = expected in existing
                results["frontend"]["services"][expected] = "✅" if found else "❌"
                if not found:
                    results["summary"]["missing"].append(f"frontend/src/services/{expected}")
        
        # Cek Frontend Components
        components_path = self.frontend / "src" / "components"
        if components_path.exists():
            existing = [f.name for f in components_path.glob("*.tsx")]
            for expected in self.expected_frontend["components"]:
                found = expected in existing
                results["frontend"]["components"][expected] = "✅" if found else "❌"
                if not found:
                    results["summary"]["missing"].append(f"frontend/src/components/{expected}")
        
        # Hitung summary
        all_expected = []
        all_expected.extend([f"backend/routers/{f}" for f in self.expected_backend["routers"]])
        all_expected.extend([f"backend/services/{f}" for f in self.expected_backend["services"]])
        all_expected.extend([f"backend/collectors/{f}" for f in self.expected_backend["collectors"]])
        all_expected.extend([f"frontend/src/hooks/{f}" for f in self.expected_frontend["hooks"]])
        all_expected.extend([f"frontend/src/services/{f}" for f in self.expected_frontend["services"]])
        all_expected.extend([f"frontend/src/components/{f}" for f in self.expected_frontend["components"]])
        
        results["summary"]["total_expected"] = len(all_expected)
        results["summary"]["total_found"] = len(all_expected) - len(results["summary"]["missing"])
        results["summary"]["completion_percentage"] = (
            (results["summary"]["total_found"] / results["summary"]["total_expected"]) * 100
            if results["summary"]["total_expected"] > 0 else 0
        )
        
        return results
    
    def print_report(self, results: Dict[str, Any]):
        """Print laporan verifikasi"""
        print("=" * 80)
        print("🔍 NEMESIS MADINA - STRUKTUR VERIFICATION REPORT")
        print("=" * 80)
        print(f"📁 Root: {results['root']}")
        print(f"🕐 Timestamp: {results['timestamp']}")
        print("=" * 80)
        
        # Backend
        print("\n📦 BACKEND")
        print("-" * 40)
        print(f"Status: {results['backend']['status']}")
        
        print("\n📂 Routers:")
        for name, status in results["backend"]["routers"].items():
            print(f"  {status} {name}")
        
        print("\n📂 Services:")
        for name, status in results["backend"]["services"].items():
            print(f"  {status} {name}")
        
        print("\n📂 Collectors (target baru):")
        for name, status in results["backend"]["collectors"].items():
            print(f"  {status} {name}")
        
        print("\n📂 WebSocket:")
        for name, status in results["backend"]["websocket"].items():
            print(f"  {status} {name}")
        
        # Frontend
        print("\n" + "=" * 80)
        print("🎨 FRONTEND")
        print("-" * 40)
        print(f"Status: {results['frontend']['status']}")
        
        print("\n📂 Hooks:")
        for name, status in results["frontend"]["hooks"].items():
            print(f"  {status} {name}")
        
        print("\n📂 Services:")
        for name, status in results["frontend"]["services"].items():
            print(f"  {status} {name}")
        
        print("\n📂 Components:")
        for name, status in results["frontend"]["components"].items():
            print(f"  {status} {name}")
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 SUMMARY")
        print("-" * 40)
        print(f"Total Expected: {results['summary']['total_expected']}")
        print(f"Total Found: {results['summary']['total_found']}")
        print(f"Completion: {results['summary']['completion_percentage']:.1f}%")
        
        if results["summary"]["missing"]:
            print(f"\n❌ Missing Files ({len(results['summary']['missing'])}):")
            for file in results["summary"]["missing"]:
                print(f"  - {file}")
        else:
            print("\n✅ All expected files found!")
        
        print("=" * 80)
    
    def save_report(self, results: Dict[str, Any], filename: str = "structure_report.json"):
        """Simpan laporan ke file JSON"""
        report_path = self.root / filename
        with open(report_path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n📄 Report saved to: {report_path}")


def main():
    """Main function"""
    # Cari root proyek (dari lokasi skrip atau current directory)
    script_dir = Path(__file__).parent if "__file__" in dir() else Path.cwd()
    
    # Coba cari root proyek (yang memiliki backend/ dan frontend/)
    root = script_dir
    while root != root.parent:
        if (root / "backend").exists() and (root / "frontend").exists():
            break
        root = root.parent
    
    print(f"🔍 Scanning project at: {root}")
    
    verifier = StructureVerifier(str(root))
    results = verifier.check_structure()
    verifier.print_report(results)
    verifier.save_report(results)


if __name__ == "__main__":
    main()