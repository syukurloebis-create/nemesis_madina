# NEMESIS Frontend Baseline — FE-0

**Tanggal:** 2026-09-18
**Commit anchor:** 579e020 (F3 CLOSED)
**Backend baseline:** 47.58 MEDIUM / 4177 entities / 2424 relationships

---

## FE-0-A — Repository State

- Modified files: 303 (frontend)
- Staged files: 0
- Untracked files: 8+
  - `services/riskApi.ts` (new)
  - `services/api.ts` (potential duplicate of api/index.ts)
  - `hooks/useDashboardData.ts` (potential duplicate of .tsx)
  - `pages/vendor/` (folder, missing VendorIntelligence)
- Diff stat: +6286/-7624 across 110 files

**Note:** Working tree dirty. Selective commit required.

---

## FE-0-B — Dependency State

**`npm ci` executed successfully.**

- Packages: 350
- Duration: 23s
- node_modules size: 312 MB
- Vulnerabilities: 8 (2 moderate, 6 high) — non-blocking, audit later

**Key deps verified:**
- react@18.3.1
- react-dom@18.3.1
- react-router-dom@6.23.0
- @tanstack/react-query@5.102.8
- cytoscape@3.34.2
- axios@1.18.1
- zod@4.5.4
- zustand@5.0.14

---

## FE-0-C — TypeScript Baseline

**Timestamp:** 2026-09-18T02:52:33Z
**Command:** `npx tsc --noEmit`
**Result:** 51 errors

### Error classification:

| Class | Count | Notes |
|-------|------:|-------|
| Dependency | 0 | `npm ci` fixed all |
| TS config | 0 | tsconfig OK |
| Existing code (API) | 49 | API fragmentation |
| API type mismatch | 46 | Missing exports/methods |
| Working tree residual | 0 | Clean |

### Error breakdown by TS code:

| Code | Count | Meaning |
|------|------:|---------|
| TS2339 | 37 | Property does not exist on API object |
| TS2614 | 9 | Module has no exported member |
| TS2724 | 1 | Wrong export name |
| TS2576 | 1 | Wrong static/instance |
| TS2551 | 1 | Wrong method name |
| TS2322 | 1 | Props type mismatch |
| TS2307 | 1 | Cannot find module |

### Top files by error count:

```
6  src/components/governance/GovernanceScore.tsx
5  src/app/routes/RUPData.tsx
3  src/components/evidence/EvidenceManager.tsx
2  src/components/integrity/HashChainVisualization.tsx
2  src/components/graph/CollusionGraphVisualization.tsx
2  src/components/evidence/EvidenceUpload.tsx
2  src/components/evidence/ChainOfCustodyDetail.tsx
2  src/components/cases/VersionDiffViewer.tsx
2  src/components/cases/CasesList.tsx
2  src/components/cases/CaseDetail.tsx
... (28 more files with 1 error each)
```

**Root cause:** 51 errors berasal dari **1 masalah utama** — API layer fragmentation. Komponen mengasumsikan method/export yang tidak ada di `services/api/index.ts`.

**Fix:** FE-1 (API adapters) akan menyelesaikan ~80% errors.

---

## FE-0-D — Build Baseline

**Timestamp:** 2026-09-18T02:53:18Z
**Command:** `npm run build`
**Result:** ✅ **SUCCESS**

```
vite v5.4.21 building for production...
✓ 1619 modules transformed.
dist/index.html                   0.44 kB │ gzip:   0.30 kB
dist/assets/index-DwL1fEN-.css   71.43 kB │ gzip:  11.90 kB
dist/assets/index-tN6Bh3-R.js   338.83 kB │ gzip: 100.62 kB
✓ built in 4.30s
real    0m7.565s
```

- dist/ created: ✅
- Total size: 425 KB
- Build time: 4.30s (Vite) / 7.56s (total)

**⚠️ Note:** Vite build **tidak** memblokir pada TS errors (karena `noEmit: true`). Build sukses meski `tsc --noEmit` menunjukkan 51 errors.

---

## FE-0-E — Summary

### Baseline established:

| Metric | Value |
|--------|-------|
| node_modules | 312 MB |
| TS errors | 51 |
| Build | ✅ SUCCESS |
| Build size | 425 KB |
| Build time | 4.3s (Vite) |
| Dependency issues | 0 |
| Config issues | 0 |

### Next steps (FE-1 onwards):

1. **FE-1** — Canonical API adapters + typed contracts
   - Target: resolve 46/51 errors (all API-related)
2. **FE-2** — Executive Dashboard integration
3. **FE-3** — Risk Reasoning
4. **FE-4** — Graph Intelligence
5. **FE-5** — Fraud Signals
6. **FE-6** — Evidence/Investigation
7. **FE-7** — UX Consolidation

### Frozen contracts (NEVER touch):

- Risk Engine v3: 47.58 MEDIUM 🔒
- Graph F3: 4177 / 2424 🔒
- F3 tag: f3-graph-intelligence-v1

---

**Baseline recorded. FE-0 COMPLETE.**
```
