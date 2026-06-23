"""
API v1 Router - NEMESIS V8+
"""

import sys
import io
from fastapi import APIRouter

# Set encoding untuk Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Create router first
router = APIRouter()

# Import modules dengan try-except
try:
    from api.v1 import cases
    router.include_router(cases.router, prefix="/cases", tags=["Cases"])
    print("[OK] Cases router loaded")
except Exception as e:
    print(f"[WARN] Cases router failed: {e}")

try:
    from api.v1 import evidence
    router.include_router(evidence.router, prefix="/evidence", tags=["Evidence"])
    print("[OK] Evidence router loaded")
except Exception as e:
    print(f"[WARN] Evidence router failed: {e}")

try:
    from api.v1 import graph
    router.include_router(graph.router, prefix="/graph", tags=["Graph"])
    print("[OK] Graph router loaded")
except Exception as e:
    print(f"[WARN] Graph router failed: {e}")

try:
    from api.v1 import fraud
    router.include_router(fraud.router, prefix="/fraud", tags=["Fraud"])
    print("[OK] Fraud router loaded")
except Exception as e:
    print(f"[WARN] Fraud router failed: {e}")

try:
    from api.v1 import risk
    router.include_router(risk.router, prefix="/risk", tags=["Risk"])
    print("[OK] Risk router loaded")
except Exception as e:
    print(f"[WARN] Risk router failed: {e}")

try:
    from api.v1 import intelligence
    router.include_router(intelligence.router, prefix="/intelligence", tags=["Intelligence"])
    print("[OK] Intelligence router loaded")
except Exception as e:
    print(f"[WARN] Intelligence router failed: {e}")

try:
    from api.v1 import procurement
    router.include_router(procurement.router, prefix="/procurement", tags=["Procurement"])
    print("[OK] Procurement router loaded")
except Exception as e:
    print(f"[WARN] Procurement router failed: {e}")

try:
    from api.v1 import recommendations
    router.include_router(recommendations.router, prefix="/recommendations", tags=["Recommendations"])
    print("[OK] Recommendations router loaded")
except Exception as e:
    print(f"[WARN] Recommendations router failed: {e}")

try:
    from api.v1 import alerts
    router.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
    print("[OK] Alerts router loaded")
except Exception as e:
    print(f"[WARN] Alerts router failed: {e}")

try:
    from api.v1 import vendors
    router.include_router(vendors.router, prefix="/vendors", tags=["Vendors"])
    print("[OK] Vendors router loaded")
except Exception as e:
    print(f"[WARN] Vendors router failed: {e}")

try:
    from api.v1 import dashboard
    router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
    print("[OK] Dashboard router loaded")
except Exception as e:
    print(f"[WARN] Dashboard router failed: {e}")

try:
    from api.v1 import auth
    router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
    print("[OK] Auth router loaded")
except Exception as e:
    print(f"[WARN] Auth router failed: {e}")

try:
    from api.v1 import health
    router.include_router(health.router, prefix="/health", tags=["Health"])
    print("[OK] Health router loaded")
except Exception as e:
    print(f"[WARN] Health router failed: {e}")

try:
    from api.v1 import metrics
    router.include_router(metrics.router, prefix="/metrics", tags=["Metrics"])
    print("[OK] Metrics router loaded")
except Exception as e:
    print(f"[WARN] Metrics router failed: {e}")

try:
    from api.v1 import export
    router.include_router(export.router, prefix="/export", tags=["Export"])
    print("[OK] Export router loaded")
except Exception as e:
    print(f"[WARN] Export router failed: {e}")

try:
    from api.v1 import integrity
    router.include_router(integrity.router, prefix="/integrity", tags=["Integrity"])
    print("[OK] Integrity router loaded")
except Exception as e:
    print(f"[WARN] Integrity router failed: {e}")

try:
    from api.v1 import rup
    router.include_router(rup.router, prefix="/rup", tags=["RUP"])
    print("[OK] RUP router loaded")
except Exception as e:
    print(f"[WARN] RUP router failed: {e}")

try:
    from api.v1 import snapshot
    router.include_router(snapshot.router, prefix="/snapshots", tags=["Snapshots"])
    print("[OK] Snapshot router loaded")
except Exception as e:
    print(f"[WARN] Snapshot router failed: {e}")

print("[OK] API v1 router registered successfully")
