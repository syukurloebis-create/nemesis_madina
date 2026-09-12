# NEMESIS Risk Engine — Canonical Contract v3

**Status:** FROZEN  
**Tanggal:** 2026-09-11  
**Baseline:** 47.58 MEDIUM (regression anchor)

---

## 1. Canonical Risk Engine

### Engine
`backend.intelligence.service.IntelligenceService.calculate()`

### Signature
```python
@classmethod
def calculate(
    cls,
    findings_risk: float = 0,
    graph_risk: float = 0,
    fraud_risk: float = 0,
    evidence_risk: float = 0,
    weights: Optional[Dict[str, float]] = None,
) -> RiskResult
```

### Formula
```
score = findings_risk * 0.30
      + graph_risk    * 0.25
      + fraud_risk    * 0.30
      + evidence_risk * 0.15
```

### Semantik Input
Semua input adalah **risk-direction**:
- `0` = tidak berisiko
- `100` = risiko maksimum

**Tidak ada** komponen `trust` yang diterima langsung. Konversi `trust → risk` dilakukan di caller.

### Level Thresholds
| Level | Range |
|-------|-------|
| `CRITICAL` | `score >= 80` |
| `HIGH` | `60 <= score < 80` |
| `MEDIUM` | `40 <= score < 60` |
| `LOW` | `score < 40` |

### Weights Canonical
| Component | Weight |
|-----------|--------|
| findings  | 0.30   |
| graph     | 0.25   |
| fraud     | 0.30   |
| evidence  | 0.15   |
| **Total** | **1.00** |

Validasi: `abs(sum - 1.0) <= 0.01`.

### RiskResult
```python
@dataclass(frozen=True)
class RiskResult:
    score: float
    level: str
    components: Dict[str, float]  # findings_risk, graph_risk, fraud_risk, evidence_risk
    weights: Dict[str, float]
    factors: List[str]
    recommendations: List[str]
```

Validasi:
- `0 <= score <= 100`
- `level in {LOW, MEDIUM, HIGH, CRITICAL}`

---

## 2. Canonical Write Path

### Endpoint
`POST /api/v1/risk/calculate/{case_id}?fraud_score={float}`

### Router
`backend.routers.risk.calculate_risk`

### Alur
```
POST /risk/calculate/{case_id}
        │
        ▼
   Risk Router
        │
        ├── findings_risk  ← inline SQL dari tabel `findings`
        ├── graph_risk     ← inline formula dari `dashboard_view.latest_graph`
        ├── fraud_risk     ← query parameter
        └── evidence_risk  ← inline SQL dari tabel `evidence`
        │
        ▼
IntelligenceService.calculate()
        │
        ▼
   RiskResult
        │
        ▼
risk_scores (INSERT ... ON CONFLICT (case_id) DO UPDATE)
        │
        ▼
dashboard_view (UPDATE latest_risk, risk_score, risk_level)
```

### Formula `findings_risk` (Router — Canonical)
```python
if total_findings == 0:
    findings_risk = 0
else:
    findings_risk = min(100, (critical_findings * 30) + (high_findings * 15))
```

### Formula `graph_risk` (Router — Canonical Production)
```python
if graph_entities > 0:
    density = graph_relationships / graph_entities
    graph_risk = min(100, (graph_entities * 0.05) + (density * 10))
else:
    graph_risk = 0
```

**Catatan:** formula ini **aggressive** — graph dengan >2000 entities akan saturasi ke `100`. Ini adalah **keputusan sadar** untuk konteks forensic risk scoring.

### Formula `evidence_risk` (Router — Canonical)
```python
if total_ev > 0:
    evidence_trust = (avg_trust * 0.7) + ((verified_ev / total_ev) * 100 * 0.3)
    evidence_risk = 100 - evidence_trust
else:
    evidence_risk = 0   # NO_DATA ≠ MAXIMUM_RISK
```

### Formula `fraud_risk` (Router — Canonical)
Diterima langsung dari query parameter `fraud_score`.

---

## 3. NO_DATA Semantics

**Prinsip:** `NO_DATA ≠ MAXIMUM_RISK`

### Evidence NO_DATA
- `total_ev == 0` → `evidence_risk = 0`
- **Bukan** `evidence_risk = 100`
- Alasan: tidak adanya evidence berarti "belum diinvestigasi", bukan "risiko tinggi"

### Findings NO_DATA
- `total_findings == 0` → `findings_risk = 0`

### Graph NO_DATA
- `graph_entities == 0` → `graph_risk = 0`

### Konsekuensi
Score akhir **lebih rendah** saat NO_DATA dibandingkan false positive `evidence_risk = 100`.

---

## 4. Persistence Contract

### Table `risk_scores`

#### Canonical Columns (v3)
| Column | Type | Nullable | Deskripsi |
|--------|------|----------|-----------|
| `findings_risk` | `float8` | YES | Risk contribution dari findings |
| `graph_risk` | `float8` | YES | Risk contribution dari graph |
| `fraud_risk` | `float8` | YES | Risk contribution dari fraud |
| `evidence_risk` | `float8` | YES | Risk contribution dari evidence |
| `components` | `json` | YES | Full snapshot components |
| `weights` | `json` | YES | Weights yang dipakai |

#### Legacy Columns (Deprecated)
| Column | Type | Status |
|--------|------|--------|
| `anomaly_score` | `float8` | DEPRECATED — alias untuk `findings_risk` |
| `collusion_score` | `float8` | DEPRECATED — alias untuk `graph_risk` |
| `financial_score` | `float8` | DEPRECATED — alias untuk `fraud_risk` |
| `temporal_score` | `float8` | DEPRECATED — belum diimplementasikan |

#### Core Columns
| Column | Type | Nullable |
|--------|------|----------|
| `id` | `varchar` | NO (PK) |
| `case_id` | `uuid` | NO (FK → cases.id, UNIQUE) |
| `overall_score` | `float8` | NO |
| `risk_level` | `risklevel` | NO |
| `factors` | `json` | YES |
| `recommendations` | `json` | YES |
| `calculated_at` | `timestamptz` | YES |
| `calculated_by` | `varchar` | YES |

#### Constraints
- `risk_scores_pkey` — PRIMARY KEY (`id`)
- `uq_risk_scores_case_id` — UNIQUE (`case_id`)
- `risk_scores_case_id_fkey` — FOREIGN KEY → `cases(id)` ON DELETE CASCADE

#### Idempotency
- `INSERT ... ON CONFLICT (case_id) DO UPDATE` menjamin **1 row per case**
- Concurrent requests aman karena unique constraint

### ORM Model
`backend.intelligence.models.RiskScore`

**Sync dengan DB:** 21 kolom (core + canonical + legacy).

### Enum `risklevel`
```
CRITICAL, HIGH, MEDIUM, LOW, INFO
```
(UPPERCASE di DB)

**Catatan:** Python enum `RiskLevel` di `intelligence/models.py` menggunakan lowercase (`"critical"`, `"high"`, dst) — mismatch dengan DB. **Tidak masalah** karena router pakai raw SQL + `CAST(:level AS risklevel)` dengan string uppercase. **ORM belum dipakai untuk write.**

---

## 5. Canonical Read Path

### Dashboard
- `dashboard_view.risk_score` — scalar
- `dashboard_view.latest_risk` — JSON snapshot
- Di-update oleh router `/risk/calculate` via `UPDATE dashboard_view`

### `/risk/explanations/{case_id}`
- Baca dari `risk_scores` via raw SQL
- Mengembalikan legacy columns: `anomaly_score`, `collusion_score`, `financial_score`, `temporal_score`

### `/risk/stats`
- Agregat dari `risk_scores`
- Distribution by `risk_level`

---

## 6. Alternative Write Path (Prepared, Deferred)

### Service
`backend.services.risk_application_service.RiskApplicationService`

### Factory
`backend.bootstrap.risk_factory.RiskFactory.create(session_maker)`

### Status
**Bekerja end-to-end, tapi BELUM dipakai untuk `/risk/calculate`.**

### Formula `graph_risk` (Service — Alternative)
```python
entity_score = min(100, entities * 0.05)
relationship_score = min(100, density * 10)
graph_risk = entity_score * 0.40 + relationship_score * 0.60
```

**Berbeda dari router formula** — lihat P1.10 technical debt.

### Kapan Dipakai
- Batch calculation (scheduler)
- CLI tool
- Event handler
- **Bukan** untuk endpoint `/risk/calculate` (saat ini)

### Kontrak
- Input: `case_id`, `fraud_score`, `weights` (optional)
- Output: `Dict[str, Any]` (hasil `RiskResult.to_dict()`)
- Transaction: single UoW per call

---

## 7. Evidence Quality State (P1.3-B)

### Property
`EvidenceVerification.quality_state`  
`EvidenceSummary.quality_state`

### Values
```
NO_DATA, LOW_QUALITY, UNVERIFIED, PARTIAL, VERIFIED, HIGH_CONFIDENCE
```

### Rules
```
1. total_count == 0                                 → NO_DATA
2. verified_count == 0 AND
   (avg_trust < 30 OR avg_confidence < 30)          → LOW_QUALITY
3. verified_count == 0                              → UNVERIFIED
4. verified_count < total_count                     → PARTIAL
5. verified_count == total_count AND
   avg_trust >= 80 AND avg_confidence >= 80         → HIGH_CONFIDENCE
6. verified_count == total_count                    → VERIFIED
```

### Catatan
- **Computed property**, bukan field persisted
- **Tidak** menambah enum baru di domain layer (menghindari fragmentasi)
- **Tidak** mengubah DB schema
- Konsisten antara `EvidenceVerification` dan `EvidenceSummary`

### API Exposure
`SummaryPresenter.evidence_to_dict()` mengembalikan `quality_state`.

---

## 8. Regression Anchor

### Case
`b4897392-87ab-4e7a-84b6-90228f3d1eb9`

### Input
```
POST /api/v1/risk/calculate/b4897392-87ab-4e7a-84b6-90228f3d1eb9?fraud_score=75.27
```

### Expected Response
```json
{
  "status": "OK",
  "case_id": "b4897392-87ab-4e7a-84b6-90228f3d1eb9",
  "result": {
    "score": 47.58,
    "level": "MEDIUM",
    "components": {
      "findings_risk": 0,
      "graph_risk": 100,
      "fraud_risk": 75.27,
      "evidence_risk": 0
    },
    "weights": {
      "findings": 0.30,
      "graph": 0.25,
      "fraud": 0.30,
      "evidence": 0.15
    }
  }
}
```

### Expected DB
```
overall_score = 47.58
risk_level = MEDIUM
findings_risk = 0
graph_risk = 100
fraud_risk = 75.27
evidence_risk = 0
calculated_by = API
```

**Baseline ini harus dipertahankan di semua regression test.**

---

## 9. Frozen Decisions

Keputusan berikut **FROZEN** dan tidak boleh diubah tanpa sprint khusus:

1. **Formula canonical** — 4 komponen, weights 30/25/30/15
2. **`evidence_risk = 0` saat NO_DATA** — bukan 100
3. **Router `/risk/calculate` sebagai canonical write path**
4. **`ON CONFLICT (case_id)` untuk idempotency**
5. **Legacy columns dipertahankan** untuk backward compatibility
6. **`quality_state` sebagai computed property** — bukan enum baru
7. **`RiskApplicationService` sebagai alternative path** — bukan canonical

---

## 10. Technical Debt (Deferred)

| # | Item | Prioritas | Deskripsi |
|---|------|-----------|-----------|
| P1.3-C | Missing Component Weight Redistribution | Medium | `evidence_risk = None` → redistribusi bobot proporsional |
| P1.3-D | Graph Semantics | Medium | Ganti formula saturasi dengan `CollusionDetector` |
| P1.7 | EvidenceStatus Fragmentation | Medium | 3 definisi berbeda (`domain/shared/enums.py`, `evidence/models.py`, `evidence/registry.py`) |
| P1.8 | Naming Consistency | Low | `IntelligenceService` vs `IntelligenceDomainService` |
| P1.9 | SQLRepository API Consistency | Medium | `SQLRepository()` vs `SQLRepository().initialize()` rawan bug |
| P1.10 | Graph Formula Unification | Low | Router (aggressive) vs Service (weighted) |

**Catatan:** Technical debt **terdokumentasi**, bukan **diabaikan**. Setiap item punya konteks dan prioritas.

---

## 11. File Reference

### Core
- `backend/intelligence/service.py` — Canonical risk engine
- `backend/routers/risk.py` — Canonical write path
- `backend/intelligence/models.py` — ORM RiskScore

### Persistence
- `backend/repositories/sqlalchemy/risk_command_repository_impl.py` — Write via ORM (untuk service)
- `backend/mappers/risk_projection_mapper.py` — Map RiskResult → projection data

### Alternative Path
- `backend/services/risk_application_service.py` — Alternative orchestration
- `backend/bootstrap/risk_factory.py` — Factory untuk service
- `backend/services/risk_projection_service.py` — Pure orchestration projection

### Evidence
- `backend/domain/value_objects/evidence_verification.py` — Domain VO + `quality_state`
- `backend/domain/summary_objects.py` — `EvidenceSummary` + `quality_state`
- `backend/calculators/evidence_score_calculator.py` — Evidence calculator
- `backend/presenters/summary_presenter.py` — API presenter

### SQL
- `backend/sql/dashboard/graph/summary.sql`
- `backend/sql/dashboard/evidence/summary.sql`
- `backend/sql/dashboard/fraud/summary.sql`
- `backend/sql/dashboard/fraud/patterns.sql`
- `backend/sql/dashboard/risk/summary.sql`
- `backend/sql/dashboard/procurement/summary.sql`

---

## 12. Change Log

| Versi | Tanggal | Perubahan |
|-------|---------|-----------|
| v1 | — | Initial risk engine |
| v2 | — | Migration ke 4 komponen (sebagian) |
| **v3** | **2026-09-11** | **Canonical contract, NO_DATA fix, provenance, idempotency** |

---

**Contract v3 — FROZEN pada 2026-09-11.**

Setiap perubahan pada kontrak ini memerlukan **sprint khusus** dengan:
- Audit dampak
- Regression test
- Update versi contract
- Update `CONTRACT.md`

---

*Dokumen ini adalah artefak resmi sprint P0–P1.2.*  
*Baseline: 47.58 MEDIUM — regression anchor.*
```
