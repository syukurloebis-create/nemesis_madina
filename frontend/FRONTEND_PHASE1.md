# NEMESIS Frontend — Phase 1 Milestone

**Status:** CLOSED  
**Tanggal:** 2026-09-11  
**Baseline:** 47.58 MEDIUM (frozen, consistent dengan backend canonical v3)

---

## Ringkasan

Phase 1 menyelesaikan **fondasi frontend intelligence platform**:

- F0.1 — API Path Normalization
- F0.1-HC — Health Check
- F0.2 — Risk Reasoning
- F1 — Executive Overview

**Functional regression PASS.** Frontend menampilkan data canonical yang konsisten dengan backend.

---

## F0.1 — API Path Normalization

### Yang Dilakukan

1. **Konvensi path** — semua service pakai `/v1/...`
2. **`client.ts` baseURL** = `/api`
3. **ENV files** konsisten (`/api` di semua environment)
4. **Volume mount nginx** → `frontend/dist:ro`
5. **62 endpoints** di 17 file dinormalisasi

### Verifikasi


### File yang Diubah

- `frontend/src/services/api/index.ts` (13 endpoints)
- `frontend/src/services/api/alerts.ts`
- `frontend/src/services/api/cases.ts`
- `frontend/src/services/api/evidence.ts`
- `frontend/src/services/api/fraud.ts`
- `frontend/src/services/api/graph.ts`
- `frontend/src/services/api/intelligence.ts`
- `frontend/src/services/api/provenance.ts`
- `frontend/src/services/api/recommendations.ts`
- `frontend/src/services/api/risk.ts`
- `frontend/src/services/api/vendors.ts`
- `frontend/src/services/decision/index.tsx`
- `frontend/src/services/decision.tsx`
- `frontend/src/services/decisionApi.ts`
- `frontend/src/services/intelligence/index.tsx`
- `frontend/src/services/procurementApi.ts`
- `frontend/src/services/provenanceApi.ts`

---

## F0.1-HC — Health Check

### Masalah

Frontend memanggil `apiClient.get('/health')` + baseURL `/api` = `/api/health` → **401 Unauthorized**.

### Solusi

Health check bypass `/api` — panggil nginx `/health` langsung:

```typescript
import axios from 'axios';
const response = await axios.get('/health');

Overall Risk Score: 47.58   MEDIUM

Risk Contribution:
  Findings Risk     0.00    weight: 30%
  Graph Risk      100.00    weight: 25%   ████████████████████
  Fraud Risk       75.27    weight: 30%   ███████████████
  Evidence Risk     0.00    weight: 15%

Detected Factors:
  • High graph risk (100.0)
  • High fraud risk (75.3)

Recommended Actions:
  → 📋 Schedule follow-up review
  → 🔎 Monitor for escalation
  → 🔗 Investigate network connections for collusion patterns

Executive Intelligence Center
AI Fraud & Risk Command Platform

Risk Score: 47.58%  Risk Level: MEDIUM  Fraud: HIGH

Why This Case Matters              Overall: 47.58

Graph Risk     weight: 25%    100.00
████████████████████████████████████████  (RED)

Fraud Risk     weight: 30%    75.27
██████████████████████████████░░░░░░░░  (ORANGE)

Findings Risk  weight: 30%    0.00
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  (GRAY)

Evidence Risk  weight: 15%    0.00
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  (GRAY)

Case:   b4897392-87ab-4e7a-84b6-90228f3d1eb9
Input:  fraud_score = 75.27

Expected:
  score = 47.58
  level = MEDIUM

Components:
  findings_risk = 0.00
  graph_risk    = 100.00
  fraud_risk    = 75.27
  evidence_risk = 0.00

Weights:
  findings = 0.30
  graph    = 0.25
  fraud    = 0.30
  evidence = 0.15

