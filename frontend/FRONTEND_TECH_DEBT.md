# NEMESIS Frontend — Technical Debt

**Status:** OPEN  
**Tanggal:** 2026-09-11  
**Constraint:** Technical debt tidak boleh mengganggu Canonical Risk Engine v3 atau baseline 47.58 MEDIUM.

---

## 1. TypeScript Errors — 91 errors across 55 files

### Kategori

| # | Kategori | Jumlah | Prioritas |
|---|----------|--------|-----------|
| 1 | API Client missing methods (`get/post/request`) | 60+ | Medium |
| 2 | Missing named exports (re-export) | 15+ | Medium |
| 3 | Missing modules (file tidak ada) | 3 | Medium |
| 4 | Type mismatch (`caseId` prop) | 2 | Low |
| 5 | Lainnya | 10+ | Low |

### Contoh Error


### Rencana Fix

- **Fase 1 (kritis):** Fix 3 missing modules
- **Fase 2 (medium):** Fix API client `get/post/request`
- **Fase 3 (low):** Fix named exports, type mismatches

**Estimasi:** 5-7 jam (defer ke Phase 3 frontend).

---

## 2. Legacy `fetch()` Calls — 5 files

| File | Line | Path |
|------|------|------|
| `frontend/src/services/errorTracker.tsx` | 110 | `${VITE_API_URL}/api/v1/errors/log` |
| `frontend/src/components/analytics/RiskMetrics.tsx` | 33 | `http://localhost:8000/api/v1/risk/stats` |
| `frontend/src/components/monitoring/AlertFeed.tsx` | 64 | `/api/v1/alerts?limit=20` |
| `frontend/src/components/monitoring/SystemStatus.tsx` | 36 | `/api/v1/health` |
| `frontend/src/pages/ThreatCenter.tsx` | 98 | `http://localhost:8000/api/v1/risk/stats` |

**Rencana:** Migrasi ke `apiClient` dengan path `/v1/...`.
**Estimasi:** 1 jam.
**Prioritas:** Low.

---

## 3. Placeholder Screens — 8 screens

| # | Screen | Status | Prioritas |
|---|--------|--------|-----------|
| 1 | Graph Intelligence | Placeholder (entity counter) | **P1** |
| 2 | Fraud Signals | Placeholder ("3 signals" no render) | **P1** |
| 3 | Evidence Health | Placeholder (NO_DATA, no action) | P2 |
| 4 | Investigation Timeline | Empty | P2 |
| 5 | Investigation Workspace | Empty (no action) | P2 |
| 6 | Recovery | Placeholder | P2 |
| 7 | Decision | Placeholder | P2 |
| 8 | Recommendations | Placeholder | P2 |

**Rencana:**
- **F3** — Graph Intelligence
- **F4** — Fraud Signals
- **F5** — Evidence Health
- **F6** — Investigation Workspace
- **F7** — Decision & Recovery

---

## 4. Orphan Components

### `ExecutiveStatusRail`

File `frontend/src/components/executive/ExecutiveStatusRail.tsx` **tidak dipakai** setelah F1.

**Keputusan:** Keep sampai Phase 2 selesai.

### `RiskReasoningPanel` Duplikat

- `frontend/src/components/Intelligence/RiskReasoningPanel.tsx` — aktif
- `frontend/src/components/risk/RiskReasoningPanel.tsx` — legacy

**Keputusan:** Hapus yang legacy setelah verifikasi.

---

## Prioritas Fix

| # | Item | Prioritas | Estimasi |
|---|------|-----------|----------|
| 1 | F3 Graph Intelligence | **P1** | 2-3 jam |
| 2 | F4 Fraud Signals | **P1** | 2 jam |
| 3 | F5 Evidence Health | P2 | 1 jam |
| 4 | 91 TypeScript errors | P2 | 5-7 jam |
| 5 | F6 Investigation Workspace | P2 | 2 jam |
| 6 | 5 fetch() legacy | P3 | 1 jam |
| 7 | F7 Decision & Recovery | P3 | 2 jam |
| 8 | Cleanup orphans | P3 | 30 menit |

---

## Constraint

**JANGAN:**
- ❌ Ubah Canonical Risk Engine v3
- ❌ Ubah formula / weights
- ❌ Ubah baseline 47.58 MEDIUM
- ❌ Sentuh backend

**BOLEH:**
- ✅ Fix frontend code
- ✅ Tambah komponen baru
- ✅ Refactor frontend module
- ✅ Fix TypeScript errors (jika tidak menyentuh kontrak canonical)

---

**Technical debt terdokumentasi. Defer ke Phase 3 frontend.**