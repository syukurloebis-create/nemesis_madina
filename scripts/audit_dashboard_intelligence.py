#!/usr/bin/env python3
"""
Audit Dashboard Intelligence Analytics Service
Memastikan refactor sesuai dengan kriteria:

1. Tidak ada endpoint yang menghitung analytics sendiri
2. Tidak ada endpoint yang melakukan sorted() terhadap entities
3. Semua endpoint menggunakan DashboardResponseFactory
4. snapshot_cache bertipe DashboardSnapshot, bukan List[Dict]
5. _collect_all_snapshots() menjadi satu-satunya tempat build snapshot
"""

import ast
import sys
from pathlib import Path

# ============================================
# KONFIGURASI
# ============================================

FILE_PATH = Path("backend/services/dashboard_intelligence_analytics_service.py")
FACTORY_IMPORT = "from backend.services.dashboard_response_factory import DashboardResponseFactory"
SNAPSHOT_TYPE = "DashboardSnapshot"
COLLECT_METHOD = "_collect_all_snapshots"

# ============================================
# FUNGSI CHECK
# ============================================

def check_factory_import(content: str) -> dict:
    """Cek apakah DashboardResponseFactory di-import"""
    return {
        "name": "DashboardResponseFactory Import",
        "status": "✅" if FACTORY_IMPORT in content else "❌ FAILED",
        "detail": "Import ditemukan" if FACTORY_IMPORT in content else "Tidak ada import DashboardResponseFactory"
    }

def check_snapshot_type(content: str) -> dict:
    """Cek apakah snapshot_cache bertipe DashboardSnapshot"""
    if "snapshot_cache: DashboardSnapshot" in content:
        return {
            "name": "snapshot_cache Type",
            "status": "✅",
            "detail": "Bertipe DashboardSnapshot"
        }
    elif "snapshot_cache: list" in content.lower() or "snapshot_cache = []" in content:
        return {
            "name": "snapshot_cache Type",
            "status": "❌ FAILED",
            "detail": "Bertipe List atau dict (bukan DashboardSnapshot)"
        }
    else:
        return {
            "name": "snapshot_cache Type",
            "status": "⚠️",
            "detail": "Tidak ditemukan atau tidak jelas"
        }

def check_collect_method(content: str) -> dict:
    """Cek apakah _collect_all_snapshots() ada"""
    if COLLECT_METHOD in content:
        return {
            "name": "_collect_all_snapshots()",
            "status": "✅",
            "detail": "Method ditemukan"
        }
    else:
        return {
            "name": "_collect_all_snapshots()",
            "status": "❌ FAILED",
            "detail": "Method tidak ditemukan"
        }

def check_manual_analytics(content: str) -> dict:
    """
    Cek apakah ada perhitungan analytics manual di endpoint
    Cek pola: risk_summary, investigation_health, evidence_health, ranking
    """
    patterns = [
        ("risk_summary = {", "Ada perhitungan risk_summary manual"),
        ("investigation_health = {", "Ada perhitungan investigation_health manual"),
        ("evidence_health = {", "Ada perhitungan evidence_health manual"),
        ("ranking.append", "Ada ranking manual"),
        ("ranking.sort", "Ada sorting manual"),
        ("top_entities.sort", "Ada sorting manual entities"),
    ]

    found = []
    for pattern, desc in patterns:
        if pattern in content:
            found.append(desc)

    return {
        "name": "Manual Analytics Calculation",
        "status": "✅" if not found else "❌ FAILED",
        "detail": "Tidak ada perhitungan manual" if not found else f"Ditemukan: {', '.join(found)}"
    }

def check_sorted_entities(content: str) -> dict:
    """Cek apakah ada sorted() terhadap entities"""
    if "sorted(" in content and "entities" in content:
        return {
            "name": "sorted() on entities",
            "status": "❌ FAILED",
            "detail": "Ada penggunaan sorted() pada entities"
        }
    else:
        return {
            "name": "sorted() on entities",
            "status": "✅",
            "detail": "Tidak ada sorted() pada entities"
        }

def parse_ast(content: str) -> dict:
    """AST Parse untuk deteksi lebih akurat"""
    try:
        tree = ast.parse(content)

        factory_used = False
        collect_method_found = False
        manual_analytics = []

        for node in ast.walk(tree):
            # Cek apakah ada import DashboardResponseFactory
            if isinstance(node, ast.ImportFrom):
                if node.module and "dashboard_response_factory" in node.module:
                    for alias in node.names:
                        if alias.name == "DashboardResponseFactory":
                            factory_used = True

            # Cek apakah ada method _collect_all_snapshots
            if isinstance(node, ast.FunctionDef):
                if node.name == "_collect_all_snapshots":
                    collect_method_found = True

            # Cek apakah ada perhitungan manual di dalam method endpoint
            if isinstance(node, ast.FunctionDef):
                if any(name in node.name for name in ["get_overview", "get_top_risk_entities"]):
                    for child in ast.walk(node):
                        # Cek assignment ke variable analytics
                        if isinstance(child, ast.Assign):
                            for target in child.targets:
                                if isinstance(target, ast.Name):
                                    if target.id in ["risk_summary", "investigation_health", "evidence_health"]:
                                        manual_analytics.append(target.id)

        return {
            "factory_used": factory_used,
            "collect_method_found": collect_method_found,
            "manual_analytics": manual_analytics
        }
    except Exception as e:
        return {"error": str(e)}

# ============================================
# MAIN AUDIT
# ============================================

def main():
    print("=" * 60)
    print("AUDIT DASHBOARD INTELLIGENCE ANALYTICS SERVICE")
    print("=" * 60)

    if not FILE_PATH.exists():
        print(f"❌ FILE {FILE_PATH} TIDAK DITEMUKAN")
        return

    content = FILE_PATH.read_text(encoding="utf-8")

    ast_result = parse_ast(content)

    # AST Results
    print("\n📊 AST ANALYSIS:")
    print(f"  • DashboardResponseFactory digunakan: {'✅' if ast_result.get('factory_used') else '❌'}")
    print(f"  • _collect_all_snapshots() ditemukan: {'✅' if ast_result.get('collect_method_found') else '❌'}")
    if ast_result.get('manual_analytics'):
        print(f"  • ⚠️ Analytics manual ditemukan: {', '.join(ast_result['manual_analytics'])}")
    else:
        print("  • ✅ Tidak ada analytics manual")

    # Detail Checks
    print("\n📋 DETAILED CHECKS:")
    checks = [
        check_factory_import(content),
        check_snapshot_type(content),
        check_collect_method(content),
        check_manual_analytics(content),
        check_sorted_entities(content),
    ]

    print(f"{'Status':<10} {'Check':<40} {'Detail':<50}")
    print("-" * 100)
    for check in checks:
        status = check['status']
        name = check['name'][:40]
        detail = check['detail'][:50]
        print(f"{status:<10} {name:<40} {detail:<50}")

    # Summary
    print("\n📊 SUMMARY:")
    passed = sum(1 for c in checks if c['status'] == '✅')
    failed = sum(1 for c in checks if c['status'] == '❌ FAILED')
    warning = sum(1 for c in checks if c['status'] == '⚠️')

    print(f"  ✅ Passed: {passed}/5")
    print(f"  ❌ Failed: {failed}/5")
    print(f"  ⚠️ Warning: {warning}/5")

    if failed == 0:
        print("\n🎉 AUDIT PASSED! Semua kriteria terpenuhi.")
    else:
        print("\n⚠️ AUDIT FAILED! Ada kriteria yang belum terpenuhi.")
        print("   Prioritas perbaikan:")
        for check in checks:
            if check['status'] == '❌ FAILED':
                print(f"     - {check['name']}")

if __name__ == "__main__":
    main()
