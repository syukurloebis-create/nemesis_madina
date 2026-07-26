#!/usr/bin/env python3
"""
verify_dashboard_sprint22.py

Sprint 2.2 Verification
=================================

Verifikasi menggunakan AST sehingga
tidak bergantung pada grep/string.

Run:

    python scripts/verify_dashboard_sprint22.py
"""

from pathlib import Path
import ast
import sys

ROOT = Path(__file__).resolve().parents[1]

SERVICE = (
    ROOT
    / "backend"
    / "services"
    / "dashboard_intelligence_analytics_service.py"
)

if not SERVICE.exists():
    print("Service tidak ditemukan")
    sys.exit(1)

source = SERVICE.read_text(encoding="utf8")
tree = ast.parse(source)

print("=" * 70)
print("SPRINT 2.2 VERIFICATION")
print("=" * 70)

passed = 0
failed = 0


def ok(msg):
    global passed
    passed += 1
    print(f"✅ {msg}")


def fail(msg):
    global failed
    failed += 1
    print(f"❌ {msg}")


# ==========================================================
# IMPORT
# ==========================================================

imports = set()

for node in ast.walk(tree):

    if isinstance(node, ast.ImportFrom):

        module = node.module or ""

        for alias in node.names:

            imports.add(f"{module}.{alias.name}")

required = [
    "backend.services.dashboard_snapshot.DashboardSnapshot",
    "backend.services.dashboard_snapshot_builder.dashboard_snapshot_builder",
    "backend.services.dashboard_response_factory.dashboard_response_factory",
]

for item in required:

    if item in imports:
        ok(f"Import {item}")
    else:
        fail(f"Import {item}")


# ==========================================================
# snapshot_cache annotation
# ==========================================================

snapshot_ok = (
    "Optional[DashboardSnapshot]" in source
    or "DashboardSnapshot | None" in source
)

if snapshot_ok:
    ok("snapshot_cache menggunakan DashboardSnapshot")
else:
    fail("snapshot_cache bukan DashboardSnapshot")


# ==========================================================
# Collector
# ==========================================================

functions = {
    node.name
    for node in ast.walk(tree)
    if isinstance(node, ast.AsyncFunctionDef)
}

if "_collect_all_snapshots" in functions:
    ok("_collect_all_snapshots tersedia")
else:
    fail("_collect_all_snapshots hilang")

if "_collect_all_snapshots_parallel" not in functions:
    ok("collector lama sudah dihapus")
else:
    fail("_collect_all_snapshots_parallel masih ada")


# ==========================================================
# Legacy builder
# ==========================================================

legacy_functions = {
    node.name
    for node in ast.walk(tree)
    if isinstance(node, ast.FunctionDef)
}

if "_build_response" not in legacy_functions:
    ok("_build_response lama sudah dihapus")
else:
    fail("_build_response lama masih ada")

if "_build_metadata" not in legacy_functions:
    ok("_build_metadata lama sudah dihapus")
else:
    fail("_build_metadata lama masih ada")


# ==========================================================
# Required endpoint
# ==========================================================

required_endpoints = [
    "get_dashboard_summary",
    "get_overview",
    "get_dashboard_kpi",
    "get_top_risk_entities",
    "get_risk_distribution",
    "get_intelligence_type_distribution",
    "get_evidence_health",
    "get_entity_history",
    "get_dashboard_status",
    "refresh_cache",
]

for fn in required_endpoints:

    if fn in functions:
        ok(fn)
    else:
        fail(fn)


# ==========================================================
# ResponseFactory (AST)
# ==========================================================

response_calls = 0

for node in ast.walk(tree):

    if isinstance(node, ast.Call):

        func = node.func

        if (
            isinstance(func, ast.Attribute)
            and func.attr == "build_response"
        ):
            response_calls += 1

if response_calls >= 9:
    ok("ResponseFactory digunakan")
else:
    fail("ResponseFactory belum lengkap")


# ==========================================================
# Manual Analytics Detection (AST)
# ==========================================================

manual = False

for node in ast.walk(tree):

    if isinstance(node, ast.Call):

        func = node.func

        if isinstance(func, ast.Name):

            if func.id in {
                "Counter",
                "defaultdict",
            }:
                manual = True

if not manual:
    ok("Tidak ada analytics manual")
else:
    fail("Masih ada analytics manual")


# ==========================================================
# Manual Ranking (AST)
# ==========================================================

ranking_manual = False

for node in ast.walk(tree):

    #
    # sorted(...)
    #

    if isinstance(node, ast.Call):

        if isinstance(node.func, ast.Name):

            if node.func.id == "sorted":
                ranking_manual = True

        #
        # list.sort(...)
        #

        if isinstance(node.func, ast.Attribute):

            if node.func.attr == "sort":
                ranking_manual = True

if not ranking_manual:
    ok("Tidak ada ranking manual")
else:
    fail("Masih ada ranking manual")


# ==========================================================
# Snapshot API
# ==========================================================

analytics_access = False
toprisk_access = False
entity_access = False

for node in ast.walk(tree):

    #
    # snapshot.analytics
    #

    if isinstance(node, ast.Attribute):

        if node.attr == "analytics":
            analytics_access = True

        if node.attr == "get_top_risk":
            toprisk_access = True

        if node.attr == "get_entity_by_name":
            entity_access = True

    #
    # snapshot.get_analytics()
    #

    if isinstance(node, ast.Call):

        func = node.func

        if isinstance(func, ast.Attribute):

            if func.attr == "get_analytics":
                analytics_access = True

if analytics_access:
    ok("Snapshot analytics access")
else:
    fail("Snapshot analytics access")

if toprisk_access:
    ok("snapshot.get_top_risk")
else:
    fail("snapshot.get_top_risk")

if entity_access:
    ok("snapshot.get_entity_by_name")
else:
    fail("snapshot.get_entity_by_name")


# ==========================================================
# SUMMARY
# ==========================================================

print("-" * 70)
print(f"PASSED : {passed}")
print(f"FAILED : {failed}")
print("-" * 70)

if failed == 0:
    print("🎉 Sprint 2.2 VERIFIED")
    sys.exit(0)

print("⚠️ Sprint 2.2 belum selesai")
sys.exit(1)