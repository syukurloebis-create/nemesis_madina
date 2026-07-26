#!/usr/bin/env python3
"""
audit_dashboard_router_sprint23.py

Sprint 2.3
Dashboard Router Integration Audit

Mengaudit Dashboard Intelligence Router.

Membedakan:
- Endpoint Router
- Aggregator Router

Menggunakan AST, bukan string matching.
"""

from pathlib import Path
import ast
import sys

ROOT = Path(__file__).resolve().parents[1]

ENDPOINT_ROUTERS = [
    ROOT / "backend/routers/dashboard_summary_router.py",
    ROOT / "backend/routers/dashboard_analytics_router.py",
    ROOT / "backend/routers/dashboard_entity_router.py",
]

AGGREGATOR_ROUTERS = [
    ROOT / "backend/routers/dashboard_intelligence.py",
]

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


print("=" * 70)
print("SPRINT 2.3 - DASHBOARD ROUTER AUDIT")
print("=" * 70)


# ==========================================================
# Helpers
# ==========================================================

FORBIDDEN = {
    "create_pool(",
    "RiskEngine",
    "Counter(",
    "defaultdict(",
    "SELECT ",
    "INSERT ",
    "UPDATE ",
    "DELETE ",
    "text(",
}


def has_service_import(tree):
    for node in ast.walk(tree):

        if isinstance(node, ast.ImportFrom):

            if (
                node.module
                == "backend.services.dashboard_intelligence_analytics_service"
            ):
                return True

    return False


def has_service_call(tree):
    """
    AST:
    dashboard_intelligence_analytics_service.get_xxx(...)
    """

    for node in ast.walk(tree):

        if isinstance(node, ast.Call):

            func = node.func

            if isinstance(func, ast.Attribute):

                value = func.value

                if (
                    isinstance(value, ast.Name)
                    and value.id
                    == "dashboard_intelligence_analytics_service"
                ):
                    return True

    return False


def async_count(tree):
    return sum(
        isinstance(node, ast.AsyncFunctionDef)
        for node in ast.walk(tree)
    )


def include_router_count(tree):
    count = 0

    for node in ast.walk(tree):

        if isinstance(node, ast.Call):

            func = node.func

            if (
                isinstance(func, ast.Attribute)
                and func.attr == "include_router"
            ):
                count += 1

    return count


# ==========================================================
# Endpoint Routers
# ==========================================================

for router in ENDPOINT_ROUTERS:

    print(f"\n[{router.name}]")

    if not router.exists():
        fail("File tidak ditemukan")
        continue

    source = router.read_text(encoding="utf8")
    tree = ast.parse(source)

    #
    # Import
    #

    if has_service_import(tree):
        ok("Import Analytics Service")
    else:
        fail("Analytics Service belum diimport")

    #
    # Legacy
    #

    bad = False

    for p in FORBIDDEN:

        if p in source:
            print(f"    ⚠ ditemukan: {p}")
            bad = True

    if bad:
        fail("Masih ada SQL / Legacy Logic")
    else:
        ok("Tidak ada SQL / Legacy Logic")

    #
    # Service Call
    #

    if has_service_call(tree):
        ok("Endpoint memakai service")
    else:
        fail("Endpoint belum memakai service")

    #
    # Async Endpoint
    #

    total = async_count(tree)

    if total:
        ok(f"Async Endpoints ({total})")
    else:
        fail("Tidak ada async endpoint")


# ==========================================================
# Aggregator Routers
# ==========================================================

for router in AGGREGATOR_ROUTERS:

    print(f"\n[{router.name}]")

    if not router.exists():
        fail("File tidak ditemukan")
        continue

    source = router.read_text(encoding="utf8")
    tree = ast.parse(source)

    #
    # Tidak boleh SQL
    #

    bad = False

    for p in FORBIDDEN:

        if p in source:
            print(f"    ⚠ ditemukan: {p}")
            bad = True

    if bad:
        fail("Masih ada SQL / Legacy Logic")
    else:
        ok("Tidak ada SQL / Legacy Logic")

    #
    # include_router
    #

    includes = include_router_count(tree)

    if includes >= 3:
        ok(f"include_router ({includes})")
    else:
        fail("Aggregator belum lengkap")


# ==========================================================
# Legacy dashboard_summary.py
# ==========================================================

legacy = ROOT / "backend/routers/dashboard_summary.py"

print("\n[Legacy Router]")

if legacy.exists():

    src = legacy.read_text(encoding="utf8")

    found = False

    for p in [
        "create_pool(",
        "RiskEngine",
        "SELECT ",
    ]:

        if p in src:
            print(f"    ⚠ legacy ditemukan: {p}")
            found = True

    if found:
        fail("dashboard_summary.py masih legacy")
    else:
        ok("Legacy router bersih")

else:
    ok("Legacy router tidak ditemukan")


print("\n" + "-" * 70)
print(f"PASSED : {passed}")
print(f"FAILED : {failed}")
print("-" * 70)

if failed == 0:
    print("🎉 Sprint 2.3 VERIFIED")
    sys.exit(0)

print("⚠ Sprint 2.3 belum selesai")
sys.exit(1)