# Behavioral Changelog — NEMESIS CP2.5.1

## 2026-09-19 — Phase 1: Type-Safe Navigation

**Commit:** a724d51
**Type:** Behavioral improvement (silent no-op resolved)

### Before
- onAction?.("fraud")         → silent no-op
- onAction?.("graph")         → silent no-op
- onAction?.("investigation") → navigate /investigation (valid)

### After
- onAction?.("fraud")         → switch Fraud tab (FIXED)
- onAction?.("graph")         → switch Graph tab (FIXED)
- onAction?.("investigation") → navigate (preserved)
- onAction?.("alerts")        → navigate /alerts (preserved)
- onAction?.("recovery")      → navigate /recovery (preserved)
- onAction?.("procurement")   → navigate /procurement (preserved)
- onAction?.("decisions")     → navigate /decisions (preserved)

### Type Safety
- IntelligenceTabId (8 IDs)
- AppRouteId (5 IDs)
- DashboardActionId (union)

### Route System
Two route files coexist:
- src/app/routes/index.tsx (10 routes, declarative config)
- src/App.tsx (runtime, includes /alerts, /investigation, etc.)

All navigate targets verified:
- /alerts, /investigation, /recovery, /procurement, /decisions

### Manual Test
1. Open http://localhost
2. Login: admin / Admin123!
3. Click "fraud" → Fraud tab active
4. Click "graph" → Graph tab active
5. Click "investigation" → /investigation

### Boundary
- Backend FROZEN (47.58 MEDIUM / 4177 / 2424)
- Tag f3-graph-intelligence-v1 FROZEN (579e020)
