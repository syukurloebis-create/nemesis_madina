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
## 2026-09-20 — Track 5: API Contract Tests

**Commit:** 6418770
**Type:** Test infrastructure (new)

### Added

- Zod-mirror schemas for frozen DTOs:
  - graph.schema.ts (6 Graph DTOs)
  - risk.schema.ts (Risk Engine v3 types)
- Contract tests:
  - baseline.test.ts (4 tests - frozen baseline)
  - graph.contract.test.ts (16 tests - F3 contract)
  - risk.contract.test.ts (8 tests - Risk Engine v3)
- Auth helper: helpers/auth.ts (env-driven credentials)
- Persistent localStorage mock in src/test/setup.ts

### Contract Guarantees

- GraphNodeDTO: no risk_score, no confidence, no first_seen
- GraphSummary: total_entities=4177, total_relationships=2424
- KeyActor: no risk_score
- RiskExplanation: score=47.58, risk_level=MEDIUM
- CollusionResponse: 4 structural relationships
- Zod .strict() forbids extra keys (drift detection)

### Runtime Notes

- Test environment: Node (via @vitest-environment node)
- Reason: jsdom blocks network, contract tests need real HTTP
- Test files untracked before this commit

### Baseline Clarification

Collusion = 4: Nilai ini dari graph_relationships.COLLUSION
(STRUCTURAL layer). Historical frozen provenance tidak established.
Analytical collusion_detections table tetap 0.

### Security

- Credentials via env vars (NEMESIS_TEST_USERNAME/PASSWORD)
- Tidak ada hardcoded credentials di source
- Credentials tidak di-commit

### Out of Scope (defer)

- client.ts extensive changes (separate audit)
- retryInterceptor.ts orphan investigation
- Toolchain commit (package.json, tsconfig.json)
