# 📄 DOKUMEN #2 — `NEMESIS_REFERENCE.md`

**Replace seluruh isi file dengan konten di bawah:**

## Security Incident Log

### 2026-09-21 — Admin Credential Exposure (P0)

**Type:** Credential exposure in tracked source + production bundle
**Status:** ✅ RESOLVED

**Timeline:**
- Detection: Forensic audit of bundle contents
- Remediation: 5 focused commits (7bd39ea, 11a7359, ca1a79f, da9cb33, 494cb41)
- Password rotation: Executed (old 'Admin123!' invalid)
- Bundle rebuilt: index-CP96eShg.js (0 credential strings)

**Scope:**
- Frontend source: 2 files
- Production bundle: index-C7OarUre.js (pre-fix)
- Docs/scripts/backend: 10 files
- Dead code: components/auth/Login.tsx removed

**Root cause:**
- Hardcoded default credentials in Login component
- Working tree refactor regressed pages/Login.tsx

**Verification:**
- Source map trace: definitive (0 credential files in bundle)
- Baseline: 47.58 MEDIUM intact
- Container health: 6/6 up

**Boundary:**
- Independent of Track 9 (401 investigation)
- Nginx cache defect resolved separately (commit 11a7359)
## BAGIAN I — KONTEKS PROYEK

### NEMESIS Overview

**NEMESIS** adalah **Anti-Corruption Intelligence Platform** untuk deteksi fraud pengadaan pemerintah Indonesia.

**Stack:**
- Backend: Python 3.12, FastAPI, SQLAlchemy async, PostgreSQL 15
- Frontend: React 18, TypeScript, Vite, Cytoscape.js, ECharts
- Infrastructure: Docker Compose, Nginx, Redis, Prometheus, Grafana
- Auth: JWT via `access_token`

**Working Directory:**
```
~/nemesis_madina_cp25_audit/
├── backend/
├── frontend/
├── scripts/
│   ├── F3.5_verify.sh
│   ├── F3.6_regression.sh
│   └── F3.7_commit.sh
├── CONTRACT.md
├── F3.3_GRAPH_CONTRACT.md
├── NEMESIS_REFERENCE.md
├── docker-compose.yml
└── nginx.conf
```

### Container Names

```
nemesis_madina_cp25_audit-api-1
nemesis_madina_cp25_audit-postgres-1
nemesis_madina_cp25_audit-redis-1
nemesis_madina_cp25_audit-nginx-1
nemesis_madina_cp25_audit-prometheus-1
nemesis_madina_cp25_audit-grafana-1
```

---

## BAGIAN II — REGRESSION ANCHOR (FROZEN)

### Baseline Data — NEVER MODIFY

| Aspek | Nilai | Status |
|-------|-------|--------|
| **Case ID** | `b4897392-87ab-4e7a-84b6-90228f3d1eb9` | 🔒 |
| **Risk Score** | **47.58** | 🔒 FROZEN |
| **Risk Level** | **MEDIUM** | 🔒 FROZEN |
| **findings_risk** | 0.00 | 🔒 |
| **graph_risk** | 100.00 | 🔒 |
| **fraud_risk** | 75.27 | 🔒 |
| **evidence_risk** | 0.00 | 🔒 |
| **Weights** | findings 0.30, graph 0.25, fraud 0.30, evidence 0.15 | 🔒 |
| **calculated_by** | API | 🔒 |

### Database State — Case Baseline

```
graph_entities:       4177
  procurement_record: 3629
  vendor:              548

graph_relationships:  2424
  VENDOR_HAS_PACKAGE: 2420
  COLLUSION:             4

collusion_detections:    0
```

---

## BAGIAN III — RISK ENGINE v3 (FROZEN)

### Canonical Risk Path — JANGAN DISENTUH

```
POST /api/v1/risk/calculate/{case_id}
        ↓
routers/risk.py (inline SQL)
        ↓
IntelligenceService.calculate()
        ↓
risk_scores (INSERT ... ON CONFLICT DO UPDATE)
        ↓
dashboard_view (UPDATE latest_risk)
```

### Formula Canonical

```
score = findings_risk × 0.30
      + graph_risk    × 0.25
      + fraud_risk    × 0.30
      + evidence_risk × 0.15
```

### Level Thresholds

```
CRITICAL: score >= 80
HIGH:     60 <= score < 80
MEDIUM:   40 <= score < 60
LOW:      score < 40
```

---

## BAGIAN IV — F3 GRAPH INTELLIGENCE SPRINT (CLOSED)

### Sprint Status

| Fase | Status |
|------|--------|
| F3.0 Graph Pre-flight | ✅ CLOSED |
| F3.1 Endpoint Discovery | ✅ CLOSED |
| F3.2 Graph Audit | ✅ CLOSED (PASS WITH BLOCKER) |
| F3.2-B Read Ownership | ✅ CLOSED |
| F3.3 Graph Contract | 🔒 LOCKED (HYBRID v1.1 — Truthful) |
| F3.4-A Domain Audit | ✅ DONE |
| F3.4-B Backend Read Fix | ✅ DONE |
| F3.4-C Frontend Migration | 🟡 PENDING (TS debt P2) |
| F3.5 Runtime Verification | ✅ CLOSED (ALL PASS) |
| F3.6 Regression | ✅ CLOSED (ZERO REGRESSION) |
| F3.7 F3 Freeze | ✅ CLOSED |

### Keputusan Kunci

**F3.3 Contract: OPSI C — HYBRID (Truthful v1.1)**

- ✅ Canonical: `/api/v1/graph/cases/{case_id}/...`
- ✅ Legacy (dengan case_id): **301 redirect**
- ✅ Legacy (tanpa case_id): **410 Gone**
- ✅ Legacy `collusion/{case_id}`: **410 Gone**

**F3.4-B: Domain-Honest Read Model**

- ❌ **Hapus** `risk_score` dari `GraphReadService` (GraphNode tidak punya)
- ❌ **Hapus** `confidence` dari `GraphReadService` (GraphNode tidak punya)
- ✅ **Key actor ranking**: structural (**degree**)
- ✅ **Density formula**: identik dengan `graph_risk` sub-formula

**F3.4-B: Bounded Read (v1) — Truthful**

- Full case-scoped `GraphAggregate` dimuat via `PostgresGraphRepository.get_by_case()`
- `limit` di-enforce di **application boundary** (`[:limit]`), **bukan** SQL
- **Tidak ada** DB-level pagination (offset/cursor)
- **Tidak ada** field-level filter di DB
- **Tidak ada** `search`
- Baseline 4177/2424 muat di memory → OK untuk v1
- DB-level pagination = technical debt P2

### Files Delivered

| # | File | Status |
|---|------|--------|
| 1 | `backend/services/graph_read_service.py` | ✅ COMMITTED |
| 2 | `backend/routers/graph.py` | ✅ COMMITTED |
| 3 | `F3.3_GRAPH_CONTRACT.md` | ✅ COMMITTED (v1.1) |
| 4 | `NEMESIS_REFERENCE.md` | ✅ COMMITTED |
| 5 | `scripts/F3.5_verify.sh` | ✅ COMMITTED |
| 6 | `scripts/F3.6_regression.sh` | ✅ COMMITTED |
| 7 | `scripts/F3.7_commit.sh` | ✅ COMMITTED |

### Runtime Wiring (Canonical)

```
container_builder.py
    ↓
PostgresGraphRepository(...)
    ↓
ServiceContainer(graph_repository=...)
    ↓
routers/graph.py (_get_graph_read_service)
    ↓
GraphReadService(graph_repository=...)
    ↓
PostgresGraphRepository.get_by_case(uow, case_id)
    ↓
GraphAggregate
    ↓
GraphReadService [:limit]
```

### Verification Results

**F3.5 Runtime:**
```
[1] Health check                    ✅ PASS
[2] Login                           ✅ PASS
[3] Canonical /summary              ✅ PASS (4177 / 2424)
[4] Canonical /metrics              ✅ PASS (density 0.000278)
[5] Canonical /key-actors           ✅ PASS (no risk_score/confidence)
[6] Legacy hybrid behaviour         ✅ PASS (301/410)
[7] Risk baseline anchor            ✅ PASS (47.58 MEDIUM)
```

**F3.6 Regression:**
```
[1] Risk baseline 47.58 MEDIUM      ✅ FROZEN
[2] DB state (4177 / 2424 / 0)      ✅ MATCH
[3] Canonical Graph API 7/7 → 200   ✅ PASS
[4] Risk Engine isolation           ✅ ISOLATED
[5] Legacy behaviour                ✅ 410/301
```

---

## BAGIAN V — 5-COMMIT BERTAHAP

| Commit | Hash | Scope | Files | Status |
|--------|------|-------|------:|--------|
| A | `dfa4ebe` | F16.3 Graph Entity Identity | 20 | ✅ DONE |
| B | `0e4ffca` | Risk Engine v3 Canonical (backend) | 15 | ✅ DONE |
| **C** | `579e020` | **F3 Graph Intelligence Read (TAGGED)** | **7** | ✅ DONE |
| D | — | Runtime Hardening | 2 | ⏸️ PENDING |
| E | — | Risk v3 Frontend UI (deferred) | 74 | ⏸️ PENDING |

### Commit A (F16.3) — Detail

```
Hash:       dfa4ebe
Files:      20 (15 new, 5 modified)
Insertions: +1327
Deletions:  -151
Scope:      Graph entity identity (business_key + source_id)
            + RUP → Graph bridge
            + GraphEntity migration chain
```

### Commit B (Risk v3 backend) — Detail

```
Hash:       0e4ffca
Files:      15
Insertions: +1170
Deletions:  -587
Scope:      Risk Engine v3 canonical formula
            (findings 0.30 + graph 0.25 + fraud 0.30 + evidence 0.15)
            + Migration 0b3a031d35d5
            + Canonical routers + services + mappers
            + ADR-030 compatibility update (dashboard_query.py)
            + Dead code fix (risk_factory.py)
```

### Commit C (F3) — Rencana

```
Scope:      7 file
  • F3.3_GRAPH_CONTRACT.md          (v1.1 truthful)
  • NEMESIS_REFERENCE.md            (final)
  • backend/routers/graph.py        (canonical + legacy hybrid)
  • backend/services/graph_read_service.py (bounded read)
  • scripts/F3.5_verify.sh          (runtime verification)
  • scripts/F3.6_regression.sh      (regression verification)
  • scripts/F3.7_commit.sh          (freeze script, safe-stop)

Tag:        f3-graph-intelligence-v1
Depends:    Commit A (F16.3) + Commit B (Risk v3)
```

### 12 Commits Done

| Fase | Commit | TS Errors | Description |
|------|--------|----------:|-------------|
| FE-1 | `ab1a7d8` | 15 | Typed contracts (types/risk.ts, types/graph.ts) |
| FE-2 | `cc32a97` | 15 | Executive Header + React Query |
| FE-4A | `25b03e7` | 8 | Dead code retirement (4 files, −431 lines) |
| FE-4C | `b31ea9d` | 8 | Graph Intelligence page + React Query lazy |
| FE-3 | `00737f7` | 8 | Risk Reasoning Panel (−872 lines) |
| FE-0 | `b05257e` | 8 | Toolchain stabilization (vite.config.ts) |
| FE-4B-next | `8b95fe7` | 6 | Login uses singleton instance |
| FE-4D | `9b9c430` | 3 | Overview + integrity adapters |
| FE-3-ext | `bdbe810` | 2 | InvestigationTimeline prop fix ⚠️ |
| FE-3-ext-followup | `30ba6f5` | 2 | OverviewTab action IDs align with new tab IDs |
| FE-4B | `61d050c` | 1 | IntegratedForensicDashboard retired |
| Sprint C | `513b294` | **0** | Legacy CollusionGraph retired 🎉 |

**Error trend: 51 → 0 (−100%)** 🎉

### Sprint A — CANCELLED

**Reason:** OverviewTab.tsx sudah menggunakan new IDs (`fraud`, `graph`) sebelum Sprint A dimulai. Tidak ada legacy IDs (`signals`, `network`) ditemukan.

**Discovery:** Silent regression yang di-address di `bdbe810` ternyata sudah di-resolve via `30ba6f5` (FE-3-ext-followup).

### FE-4B — DONE (Retire)

**Commit:** `61d050c`

**Action:**
- Removed: `import IntegratedForensicDashboard` from routes
- Deleted: `src/pages/integrated/IntegratedForensicDashboard.tsx`
- Backup: `/tmp/nemesis_backup/IntegratedForensicDashboard.tsx.<ts>`

**Reason:**
- Page adalah redundant aggregator (Cases + Entities + Procurement)
- No canonical `/api/v1/entities` endpoint exists (HTTP 404)
- Contract mismatch: page expects `Entity[]`, gets `GraphNodeDTO[]`
- No external navigation links

### Sprint C — DONE (Retire)

**Commit:** `513b294`

**Action:**
- Removed: `import CollusionGraph` from ProcurementIntelligence.tsx
- Removed: `<CollusionGraph />` section
- Deleted: `src/components/CollusionGraph.tsx`
- Backup: `/tmp/nemesis_backup/CollusionGraph.tsx.20260919_142619`

**Reason:**
- Legacy component (Aug 24) with self-fetching anti-pattern
- Requires `caseId` for `getGraphStats()` + `getGraphCollusion()`, not passed
- Superseded by canonical `/collusion-graph` route
- No external navigation links

### Boundary Intact

- Risk Engine v3 FROZEN (47.58 MEDIUM)
- Graph F3 FROZEN (4177 / 2424)
- GraphNodeDTO FROZEN
- Tag f3-graph-intelligence-v1 FROZEN

### Sprint C — NEXT
CollusionGraph.tsx(34,9) args mismatch.
Scope: Procurement domain.
Target: TS errors 1 → 0.

**Error trend: 51 → 0 (−100%)** 🎉
---

## BAGIAN VI — INFRASTRUCTURE

### Docker Compose — Restart Policy

```yaml
postgres:
  restart: unless-stopped
redis:
  restart: unless-stopped
api:
  restart: unless-stopped
```

### ⚠️ LESSON LEARNED — Uvicorn Reload (CRITICAL)

**`docker compose restart api` TIDAK reload code Python dari bind mount.**

- Uvicorn load module ke memory saat startup
- `restart` hanya restart proses tanpa re-import
- Bind mount sync file di **filesystem**, bukan **Python runtime**

**✅ WAJIB untuk reload:**
```bash
docker compose up -d --force-recreate api
```

**❌ JANGAN pakai untuk reload code:**
```bash
docker compose restart api   # tidak reload
```

### ⚠️ MSYS PATH TRANSLATION (Git Bash)

**Git Bash (MINGW64) menerjemahkan `/app` → `C:/Program Files/Git/app`.**

**Workaround:**
```bash
# ✅ BENAR (MSYS escape)
docker exec -w //app container cmd

# ✅ BENAR (path absolut, tanpa -w)
docker exec container cmd //app/backend/file.py

# ❌ SALAH
docker exec -w /app container cmd
```

**Atau pakai PowerShell** untuk menghindari MSYS.

### Disk Space

```
C:  3.74 GB free  (CRITICAL, maintenance only)
D:  10.35 GB free (LOW)
E:  43.12 GB free (OK)
```

**Status:** ⚠️ **Maintenance only**

**JANGAN:**
- ❌ `wsl --manage --set-sparse --allow-unsafe`
- ❌ Hapus salah satu VHDX
- ❌ `docker system prune --volumes`
- ❌ Reset Docker Desktop

---

┌─────────────────────────────────────────────────────────────────┐
│  POST-CP2.5.1 CLEANUP SPRINT (OPTIONAL)                         │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  PRIORITY 1 — Dead Code Removal:                                │
│  • backend/routers/entities.py (MOCK, unregistered)             │
│  • backend/routers/entity.py (unregistered)                     │
│  • frontend/src/components/graph/CollusionGraph.tsx (orphan)    │
│  • frontend/src/components/procurement/CollusionGraph.tsx (orphan)
│                                                                  │
│  PRIORITY 2 — Canonical Entity API:                             │
│  • Design: GET /api/v1/entities + GET /api/v1/entities/{id}     │
│  • Contract: EntityDTO with risk_score, confidence, first_seen  │
│  • Frontend: entityApi.ts                                       │
│  • DO NOT modify GraphNodeDTO                                   │
│                                                                  │
│  PRIORITY 3 — Type Safety:                                      │
│  • IntelligenceTabId union type                                 │
│  • ESLint rules for case-scoped API calls                       │
│  • OpenAPI → TypeScript codegen                                 │
│                                                                  │
│  PRIORITY 4 — Infrastructure:                                   │
│  • Docker Desktop auto-start                                    │
│  • Comprehensive DB health check                                │
│  • Disk C: > 5 GB cleanup                                       │
└─────────────────────────────────────────────────────────────────┘

// Proposed: src/domains/ structure
src/
├── domains/
│   ├── entity/
│   │   ├── types.ts       (EntityDTO)
│   │   ├── api.ts         (entityApi)
│   │   └── components/
│   ├── graph/
│   │   ├── types.ts       (GraphNodeDTO, GraphEdgeDTO)
│   │   ├── api.ts         (graphApi)
│   │   └── components/
│   ├── procurement/
│   │   ├── types.ts       (ProcurementSummary, CollusionPattern)
│   │   ├── api.ts         (procurementApi)
│   │   └── components/
│   └── case/
│       ├── types.ts       (CaseDTO)
│       ├── api.ts         (caseApi)
│       └── components/

// src/domains/entity/api.contract.test.ts
import { entityApi } from './api';
import { EntityDTOSchema } from './types';

describe('Entity API Contract', () => {
  it('should match EntityDTO schema', async () => {
    const entities = await entityApi.list();
    entities.forEach(e => {
      expect(() => EntityDTOSchema.parse(e)).not.toThrow();
    });
  });
});

// src/types/navigation.ts
export type IntelligenceTabId = 
  | 'overview' | 'risk' | 'graph' | 'fraud'
  | 'evidence' | 'timeline' | 'investigation' | 'recovery';

export type AppRouteId =
  | 'alerts' | 'investigation' | 'recovery'
  | 'procurement' | 'decisions';



## BAGIAN VII — ENVIRONMENT QUIRKS

### PostgreSQL Credentials

```
Host (dari WSL): 127.0.0.1:5432
Host (dari container): postgres:5432
User: nemesis
Password: nemesis123
Database: nemesis_db
```

### Admin Login

```
Username: admin
Password: <see .env / NEMESIS_TEST_PASSWORD>
```

### Container External Ports

| Container | Host Port |
|-----------|-----------|
| api | 8000 |
| postgres | 5432 |
| redis | 6379 |
| nginx | 80, 443 |
| prometheus | 9090 |
| grafana | 3000 |

---

## BAGIAN VIII — FILES PENTING

### Backend Core

| File | Purpose |
|------|---------|
| `backend/main.py` | FastAPI app, router registration |
| `backend/database.py` | `async_session_maker`, `get_db` |
| `backend/core/container.py` | `ServiceContainer` |
| `backend/bootstrap/container_builder.py` | Container composition root |
| `backend/infrastructure/unit_of_work.py` | `UnitOfWorkFactory`, `IUnitOfWork` |

### Risk Engine (FROZEN, Committed 0e4ffca)

| File | Purpose |
|------|---------|
| `backend/routers/risk.py` | Canonical write path |
| `backend/intelligence/service.py` | `IntelligenceService.calculate()` |
| `backend/intelligence/models.py` | `RiskScore` ORM |

### Graph Layer (F3, Committed `579e020`, tag: f3-graph-intelligence-v1)

| File | Purpose |
|------|---------|
| `backend/routers/graph.py` | Graph API (canonical + legacy hybrid) |
| `backend/services/graph_read_service.py` | Application read boundary (bounded) |
| `backend/graph/models.py` | `GraphEntity`, `GraphRelationship` ORM |
| `backend/graph/domain/aggregate.py` | `GraphAggregate` |
| `backend/graph/domain/node.py` | `GraphNode` (5 fields) |
| `backend/graph/domain/edge.py` | `GraphEdge` |
| `backend/graph/infrastructure/repositories/postgres.py` | `PostgresGraphRepository` (canonical) |
| `backend/graph/infrastructure/interfaces/repository.py` | `GraphRepository` port |
| `backend/graph/infrastructure/mappers/to_domain.py` | `OrmToGraphMapper` |

### F16.3 (Committed dfa4ebe)

| File | Purpose |
|------|---------|
| `backend/migrations/versions/add_business_key_source_id.py` | GraphEntity identity |
| `backend/migrations/versions/increase_kode_rup_length.py` | Multi-RUP support |
| `backend/graph/transformers/` | RUP → GraphNode transformers |
| `backend/services/rup_to_graph_bridge_service.py` | RUP → Graph orchestration |

### Contract & Documentation

| File | Purpose | Status |
|------|---------|--------|
| `CONTRACT.md` | Canonical Risk Engine v3 | 🔒 FROZEN |
| `F3.3_GRAPH_CONTRACT.md` | Graph Intelligence Contract v1.1 | 🔒 FROZEN |
| `NEMESIS_REFERENCE.md` | This file | 📘 |
| `docs/adr/ADR-021-Single-Graph-Runtime.md` | Single Graph Runtime | PROPOSED |
| `docs/adr/ADR-030-architecture-freeze.md` | Architecture Freeze | APPROVED |
| `docs/architecture/freeze-register.md` | Freeze register v2 | ACTIVE |

### Scripts

| File | Purpose |
|------|---------|
| `scripts/F3.5_verify.sh` | Runtime verification |
| `scripts/F3.6_regression.sh` | Regression verification |
| `scripts/F3.7_commit.sh` | Freeze script (safe-stop default) |

### Current HEAD
513b294 (HEAD -> cp2.5.1-stabilization, origin/cp2.5.1-stabilization)
feat(frontend/sprint-c): retire legacy CollusionGraph

Commits:
513b294 Sprint C (CollusionGraph retired)
61d050c FE-4B (IntegratedForensicDashboard retired)
30ba6f5 FE-3-ext-followup (OverviewTab action IDs)
bdbe810 FE-3-ext (prop fix + refactor)
9b9c430 FE-4D (overview + integrity adapters)
8b95fe7 FE-4B-next (Login singleton)
b05257e FE-0 (toolchain stabilization)
00737f7 FE-3 (Risk Reasoning Panel)
b31ea9d FE-4C (Graph Intelligence RQ)
25b03e7 FE-4A (dead code retirement)
cc32a97 FE-2 (React Query + Exec Header)
ab1a7d8 FE-1 (typed contracts)
579e020 freeze(f3): Graph Intelligence v1 — TAG
0e4ffca feat(risk): Risk Engine v3 canonical
dfa4ebe feat(f16.3): Graph entity identity
---

## BAGIAN IX — COMMANDS REFERENCE

### Login & Token

```bash
FRESH_TOKEN=$(curl -s -X POST "http://127.0.0.1:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"$NEMESIS_TEST_PASSWORD"}' | jq -r '.access_token')
```

### Test Baseline

```bash
CASE=b4897392-87ab-4e7a-84b6-90228f3d1eb9

curl -s "http://127.0.0.1:8000/api/v1/risk/explanations/$CASE" \
  -H "Authorization: Bearer $FRESH_TOKEN" | jq '{score, risk_level}'
```

**Expected:** `{"score": 47.58, "risk_level": "MEDIUM"}`

### Test Graph Canonical

```bash
# Summary
curl -s "http://127.0.0.1:8000/api/v1/graph/cases/$CASE/summary" \
  -H "Authorization: Bearer $FRESH_TOKEN" | jq .

# Key actors
curl -s "http://127.0.0.1:8000/api/v1/graph/cases/$CASE/key-actors?limit=5" \
  -H "Authorization: Bearer $FRESH_TOKEN" | jq .
```

### Docker Operations

```bash
# Status
docker compose ps

# ⚠️ FORCE RECREATE (reload code) — WAJIB setelah patch
docker compose up -d --force-recreate api

# Restart (tidak reload code)
docker compose restart api

# Logs
docker logs --tail 100 nemesis_madina_cp25_audit-api-1 2>&1
```

### DB Queries

```bash
PG=nemesis_madina_cp25_audit-postgres-1
CASE=b4897392-87ab-4e7a-84b6-90228f3d1eb9

docker exec $PG psql -U nemesis -d nemesis_db -c "
SELECT entity_type, COUNT(*) FROM graph_entities
WHERE case_id = '$CASE' GROUP BY entity_type;"

docker exec $PG psql -U nemesis -d nemesis_db -c "
SELECT relationship_type, COUNT(*) FROM graph_relationships
WHERE case_id = '$CASE' GROUP BY relationship_type;"
```

### Verification Scripts

```bash
bash scripts/F3.5_verify.sh   # runtime verification
bash scripts/F3.6_regression.sh   # regression
bash scripts/F3.7_commit.sh    # freeze (safe-stop default)
```

### Sprint Status

| Sprint | Status | Commit | Notes |
|--------|--------|--------|-------|
| Sprint A | ✅ CANCELLED | — | OverviewTab already uses new IDs |
| Sprint B | ✅ DONE | `61d050c` | FE-4B retire IntegratedForensicDashboard |
| Sprint C | ✅ DONE | `513b294` | Retire legacy CollusionGraph |
| **All FE Sprints** | ✅ **COMPLETE** | — | **TS errors: 0** 🎉 |

### Post-CP2.5.1 Backlog (Prioritized)

| # | Item | Priority | Notes |
|---|------|----------|-------|
| 1 | Consolidate orphan CollusionGraph variants | P2 | graph/, procurement/ |
| 2 | Build canonical Entity API | P1 | `/api/v1/entities` |
| 3 | Delete dead backend code | P1 | entities.py, entity.py |
| 4 | Type-safe tab navigation | P2 | IntelligenceTabId union |
| 5 | API contract tests | P2 | Prevent DTO drift |
| 6 | Docker Desktop auto-start | P1 | Infra |
| 7 | Comprehensive DB health check | P1 | Infra |
| 8 | Disk C: > 5 GB | P1 | Infra |
| 9 | Event bus fragmentation | P2 | Refactor |
| 10 | OpenAPI → TS codegen | P2 | Tooling |

### Sprint B — DONE (FE-4B)
IntegratedForensicDashboard retired.
- No canonical Entity API exists
- Page is redundant aggregator
- TS errors: 2 → 1
- Commit: <hash>

---

### Sprint A — CANCELLED (Already Done)
OverviewTab.tsx already uses new IDs (fraud, graph).
Legacy IDs (signals, network) not found in codebase.
→ No action needed.

### Sprint A-New — OPTIONAL (Post-CP2.5.1)
Issue: handleAction does not handle tab IDs (fraud, graph, etc.)
Fix: Update handleAction to route tab IDs → setActiveTab
## BAGIAN X — DO'S & DON'TS

### ✅ DO

- **Force recreate** API setelah patch backend:
  `docker compose up -d --force-recreate api`
- **Audit dulu, patch kemudian**
- **Test runtime sebelum commit**
- **Verify baseline 47.58 MEDIUM** setelah perubahan
- **Use PowerShell** untuk test API
- **Use Git Bash** untuk bash scripts
- **Commit file spesifik**, jangan `git add .`
- **Pakai `//app`** (double slash) untuk path di `docker exec` Git Bash

### ❌ DON'T

- **Jangan `docker compose restart api`** untuk reload code
- **Jangan modifikasi `risk_scores`** dari Graph
- **Jangan modifikasi `dashboard_view.latest_graph`** dari Graph
- **Jangan modifikasi `risk.py`** dari Graph
- **Jangan ubah formula canonical** Risk Engine
- **Jangan ubah weights** 30/25/30/15
- **Jangan `docker stop`** untuk test restart policy (gunakan `docker kill`)
- **Jangan jalankan `wsl --manage --set-sparse --allow-unsafe`**
- **Jangan hapus salah satu VHDX** (56 GB)
- **Jangan reset Docker Desktop** tanpa audit

---

## BAGIAN XI — TECHNICAL DEBT (Backlog)

| # | Item | Priority | Notes |
|---|------|----------|-------|
| 1 | 91 TypeScript errors di 55 files | P2 | Frontend debt |
| 2 | 5 legacy `fetch()` calls | P3 | Frontend |
| 3 | 8 placeholder screens | P2 | Frontend |
| 4 | `ExecutiveStatusRail` orphan | P3 | Frontend |
| 5 | `RiskReasoningPanel` duplikat | P3 | Frontend |
| 6 | Docker Desktop auto-start config | P1 | Infra |
| 7 | Health check komprehensif (DB) | P1 | Infra |
| 8 | Disk C: < 5 GB | P1 | Infra |
| 9 | Event bus fragmentation | P2 | Backend |
| 10 | 11 CollusionDetector consolidation | P2 | Backend |
| 11 | 5 GraphBuilder consolidation | P2 | Backend |
| 12 | 7 GraphRegenerationService consolidation | P2 | Backend |
| 13 | **DB-level pagination untuk `/entities` + `/relationships`** | P2 | Graph v1 → v2 |
| 14 | **Field-level filter** (`entity_type`, `relationship_type`, `search`) | P2 | Graph v1 → v2 |
| 15 | **Frontend Risk v3 UI migration** | P2 | 74 file |
| 16 | **Risk v3 frontend sprint** | P2 | Deferred |
| 17 | **Runtime Hardening commit (docker-compose + CONTRACT §13)** | P3 | Sprint D |

---

## BAGIAN XII — QUICK START UNTUK PERCAKAPAN BARU

### 1. Verifikasi Environment

```bash
cd ~/nemesis_madina_cp25_audit
docker compose ps
curl -s http://127.0.0.1:8000/health
```

**Expected:** 6/6 containers Up, API healthy.

### 2. Verifikasi Baseline

```bash
FRESH_TOKEN=$(curl -s -X POST "http://127.0.0.1:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"$NEMESIS_TEST_PASSWORD"}' | jq -r '.access_token')

CASE=b4897392-87ab-4e7a-84b6-90228f3d1eb9

curl -s "http://127.0.0.1:8000/api/v1/risk/explanations/$CASE" \
  -H "Authorization: Bearer $FRESH_TOKEN" | jq '{score, risk_level}'
```

**Expected:** `{"score": 47.58, "risk_level": "MEDIUM"}`

### 3. Verify Graph Canonical

```bash
curl -s "http://127.0.0.1:8000/api/v1/graph/cases/$CASE/summary" \
  -H "Authorization: Bearer $FRESH_TOKEN" | jq '{total_entities, total_relationships}'
```

**Expected:** `{"total_entities": 4177, "total_relationships": 2424}`

### 4. Runtime Verification

```bash
bash scripts/F3.5_verify.sh
bash scripts/F3.6_regression.sh
```

**Expected:** ALL PASS.

### 5. Baca Contract

```bash
cat F3.3_GRAPH_CONTRACT.md | head -100
```

### 6. Status Sprint

| Fase | Status |
|------|--------|
| P0 Canonical Risk Engine | ✅ CLOSED |
| Frontend Phase 1 | ✅ CLOSED |
| **F3 Graph Intelligence** | **🔒 FREEZE (Tag: f3-graph-intelligence-v1)** |
| F3.4-C Frontend Migration | 🟡 PENDING (P2) |
| Risk v3 Frontend UI | 🟡 PENDING (P2) |
| Runtime Hardening | 🟡 PENDING (P3) |

### 7. Next Action

**Graph Intelligence Sprint CLOSED. Sprint berikutnya:**
- F3.4-C (frontend TS debt)
- Risk v3 Frontend UI
- Runtime Hardening
- Disk cleanup (P1)

---

## BAGIAN XIII — CHANGE LOG

| Versi | Tanggal | Perubahan |
|-------|---------|-----------|
| CP2.5.1 | 2026-09-16 | Frontend Phase 1 CLOSED |
| CP2.5.1 | 2026-09-18 | F3 Graph Intelligence CLOSED (HYBRID v1.1) |
| CP2.5.1 | 2026-09-18 | F16.3 committed (dfa4ebe) |
| CP2.5.1 | 2026-09-18 | Risk v3 backend committed (0e4ffca) |
| CP2.5.1 | 2026-09-18 | F3 + tag pending (commit C) |

---

**Dokumen ini referensi lengkap untuk melanjutkan NEMESIS CP2.5.1 di percakapan baru.**

**Baseline 47.58 MEDIUM tetap FROZEN. Risk Engine v3 tidak disentuh. Graph layer read-only.**
```

## BAGIAN XIV — Current Metrics

TS errors:          0 (from 51, -100%)
FE commits:         18 (session total)
Build:              SUCCESS
Frontend status:    100% clean
Behavioral status:  All verified

Contract Tests:
  Files:            3 (baseline, graph, risk)
  Tests:            28 passing
  Coverage:         graphApi, riskApi
  Baseline:         47.58 / 4177 / 2424 / 4 collusion

Backend:            FROZEN
Risk:               47.58 MEDIUM
Graph:              4177 / 2424
Tag:                f3-graph-intelligence-v1 (annotated)
                    -> 579e020

Remote:             origin/cp2.5.1-stabilization = 6418770

### Track Completion Status

| Track | Status | Commit |
|-------|--------|--------|
| Track 1: Documentation Sync | DONE | bb70c29 |
| Track 2: Cleanup Sprint | DONE | 708c040 |
| Track 4: Type-Safe Navigation | DONE | a724d51 |
| Track 5: API Contract Tests | DONE | 6418770 |
| Track 6: Infrastructure Hardening | DONE | 796aacc |
| Track 7: Behavioral Changelog | DONE | f5316f8 |
| Track 3: Canonical Entity API | PENDING | - |
