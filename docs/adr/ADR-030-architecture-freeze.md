# \# ADR-030: Architecture Freeze of Dormant Components

# 

# \*\*Status:\*\* PROPOSED → REVIEWED → APPROVED

# \*\*Tanggal:\*\* 2026-07-23

# \*\*Penulis:\*\* Arsitek Sistem

# \*\*Reviewer:\*\* Tim Arsitektur NEMESIS

# \*\*Penyetuju:\*\* Architecture Board

# 

# \---

# 

# \## 0. Scope

# 

# ADR ini mengatur \*\*komponen arsitektur dormant\*\* yang tidak lagi menjadi bagian dari production execution path, tetapi tetap dipertahankan sebagai artefak arsitektur.

# 

# \*\*Termasuk dalam Scope:\*\*

# \- Komponen CQRS Query yang tidak aktif di runtime.

# \- Komponen Projection yang tidak aktif di runtime.

# \- Komponen Outbox yang tidak aktif di runtime.

# \- Artefak arsitektur yang masih direferensikan oleh ADR lain.

# \- Test suite yang terkait dengan komponen-komponen tersebut.

# 

# \*\*Tidak Termasuk dalam Scope (Excluded):\*\*

# \- Production services yang aktif (`RiskApplicationService`, `RiskProjectionService`, dll.).

# \- Database schema yang aktif (`events`, `snapshots`, dll.).

# \- Domain contracts yang aktif.

# \- Public REST API yang aktif.

# \- Komponen yang sedang dalam proses refactoring.

# \- Technical debt yang tidak terkait dengan arsitektur dormant.

# 

# \---

# 

# \## 1. Non Goals

# 

# ADR ini \*\*TIDAK\*\* bertujuan untuk:

# 

# \- ❌ Menggantikan program refactoring yang sedang berjalan.

# \- ❌ Menggantikan manajemen technical debt.

# \- ❌ Menggantikan kebijakan deprecation yang sudah ada.

# \- ❌ Membekukan production runtime.

# \- ❌ Membekukan evolusi database.

# \- ❌ Menyelesaikan incompatibility test yang ada (API drift, kontrak domain, dll.).

# 

# \*\*Catatan Penting:\*\* Freeze pada ADR-030 \*\*hanya membatasi evolusi komponen dormant\*\*, bukan menggantikan program migrasi kontrak API atau perbaikan test yang masih diperlukan.

# 

# \---

# 

# \## 2. Context

# 

# Audit arsitektur menyeluruh (Tahap A–D) telah mengidentifikasi beberapa komponen yang \*\*tidak menjadi bagian dari production execution path\*\*, tetapi masih memiliki keberadaan dalam:

# 

# 1\. \*\*Test Suite\*\* — Komponen masih diuji (misalnya `test\_projection.py`, `test\_outbox\_publisher.py`, `test\_command\_flow.py`).

# 2\. \*\*Domain Layer\*\* — Beberapa komponen masih menjadi bagian dari kontrak domain, meskipun tidak digunakan di runtime.

# 3\. \*\*Import Graph\*\* — Komponen masih diimpor oleh modul lain, meskipun tidak dieksekusi.

# 4\. \*\*ADR\*\* — Komponen masih disebut dalam ADR-020 dan ADR-027 sebagai bagian dari rencana arsitektur.

# 5\. \*\*Architectural Artifacts\*\* — Beberapa komponen merupakan artefak dari proses migrasi arsitektur yang masih relevan secara historis.

# 

# \*\*Kondisi Test Suite Saat Ini:\*\*

# \- 308 tests collected

# \- 47 failed tests (terutama API drift pada domain events)

# \- 57 errors (terutama missing modules dan helper functions)

# \- 3 xfailed tests (terkait dengan `AnalyzeCaseCommandHandler`)

# 

# \*\*Penyebab Utama Kegagalan Test:\*\*

# 1\. API drift pada domain events (`metadata`, `patterns`, `packages`, dll.).

# 2\. Kontrak domain yang berubah (`DomainEvent`, `FraudPayload`, `EvidencePayload`, dll.).

# 3\. Infrastruktur test yang belum lengkap (`create\_test\_session\_factory`).

# 4\. Modul yang sudah direstrukturisasi (`backend.core.events`).

# 

# \*\*Implikasi:\*\* Freeze pada ADR-030 \*\*tidak menyelesaikan incompatibility test\*\* yang ada. Freeze hanya membatasi evolusi komponen dormant, sementara perbaikan test dan migrasi kontrak API tetap menjadi tanggung jawab tim secara terpisah.

# 

# Menghapus komponen-komponen ini secara langsung akan menyebabkan:

# \- `ModuleNotFoundError` dan `ImportError` pada test suite.

# \- Hilangnya artefak arsitektur yang masih diperlukan untuk referensi historis.

# \- Risiko yang tidak perlu pada sistem yang sedang berjalan.

# 

# Oleh karena itu, diperlukan pendekatan yang lebih konservatif: \*\*Architecture Freeze\*\*.

# 

# \---

# 

# \## 3. Decision

# 

# Kami akan menerapkan strategi \*\*Architecture Freeze\*\* untuk komponen-komponen yang teridentifikasi sebagai \*\*Dormant\*\* tetapi masih memiliki jejak di test suite, domain layer, atau dokumentasi arsitektur.

# 

# \### 3.1. Prinsip Dasar

# 

# > \*\*Frozen components are not deprecated. They are intentionally preserved architectural assets.\*\*

# 

# > \*\*Freeze is a governance state rather than a lifecycle end-state.\*\*

# 

# > \*\*Frozen status applies to the architectural responsibility of a component, not to the physical source file.\*\*

# 

# Ini adalah prinsip utama yang membedakan \*\*Freeze\*\* dari \*\*Legacy\*\*:

# 

# | Konsep | Definisi | Implikasi |

# | :--- | :--- | :--- |

# | \*\*Legacy\*\* | Sistem lama yang harus diganti | Harus dihapus atau diganti |

# | \*\*Frozen\*\* | Komponen yang sengaja tidak aktif | Dipertahankan sebagai artefak arsitektur, dapat dicairkan |

# 

# Komponen Frozen \*\*bukan\*\* kode mati. Mereka adalah \*\*aset arsitektur yang sengaja dipertahankan\*\* untuk referensi, migrasi, atau kemungkinan aktivasi di masa depan.

# 

# \### 3.2. Governance Model: Model B+ — Governance Freeze with Baseline Protection

# 

# | Kondisi | Status | Alasan |

# | :--- | :--- | :--- |

# | Existing dependency (from reference commit) | ✅ PASS | Grandfathered |

# | Frozen → Frozen | ✅ PASS | Internal dependency |

# | New dependency (not in baseline) | ❌ FAIL | Architecture drift |

# | Remove dependency | ✅ PASS | Decreasing coupling |

# | Reintroduce removed dependency | ❌ FAIL | New dependency without ADR |

# | Baseline changed without ADR | ❌ FAIL | Governance bypass |

# | Baseline changed with ADR | ✅ PASS | Approved governance change |

# 

# \### 3.3. Decision Authority

# 

# | Action | Authority | Requirement |

# | :--- | :--- | :--- |

# | \*\*Freeze Component\*\* | Architecture Board | ADR-030 + Freeze Register entry |

# | \*\*Unfreeze Component\*\* | Architecture Board | New ADR explicitly revoking freeze |

# | \*\*Remove Frozen Component\*\* | Architecture Board + Tech Lead | All Future Removal Criteria met + New ADR |

# | \*\*Override Freeze\*\* | Architecture Board | New ADR explicitly overriding |

# 

# \### 3.4. Allowed Modifications

# 

# Untuk komponen Frozen, \*\*hanya\*\* modifikasi berikut yang diizinkan:

# 

# | Allowed | Not Allowed |

# | :--- | :--- |

# | ✅ Security patches | ❌ New features |

# | ✅ Python compatibility updates | ❌ Refactoring |

# | ✅ Dependency compatibility updates | ❌ Redesign |

# | ✅ Type hint updates | ❌ API changes |

# | ✅ Documentation updates | ❌ Behavior changes |

# | ✅ Import path corrections | ❌ Performance optimizations (non-critical) |

# | ✅ Build system changes | ❌ Architecture changes |

# 

# \### 3.5. Architecture Drift Rule

# 

# > \*\*Production runtime SHALL NOT introduce new compile-time, runtime, or deployment dependency on Frozen Components.\*\*

# 

# Artinya:

# \- Komponen baru \*\*tidak boleh\*\* mengimpor atau bergantung pada komponen Frozen.

# \- Jika ada kebutuhan untuk menggunakan komponen Frozen, maka komponen tersebut harus \*\*dicairkan (unfreeze)\*\* terlebih dahulu melalui ADR baru.

# \- \*\*Termasuk\*\* dalam dependency yang dicegah:

# &#x20; - Python imports (compile-time)

# &#x20; - DI Container registration (runtime)

# &#x20; - Service registration (runtime)

# &#x20; - Celery workers (runtime)

# &#x20; - Scheduler/Cron jobs (deployment)

# &#x20; - Plugin registration (deployment)

# &#x20; - Docker dependencies (deployment)

# 

# \### 3.6. Klasifikasi Komponen Frozen

# 

# Komponen Frozen dibagi menjadi \*\*dua kategori\*\*:

# 

# \#### Type A — Dormant Runtime

# 

# | ID | Komponen | File | Alasan |

# | :--- | :--- | :--- | :--- |

# | FR-001 | `GetDashboardQueryHandler` | `backend/application/queries/get\_dashboard\_handler.py` | Tidak aktif di production execution path |

# | FR-002 | `GetDashboardQuery` | `backend/application/queries/dashboard\_query.py` | Tidak aktif di production execution path |

# | FR-003 | `DashboardReadRepository` | `backend/infrastructure/repositories/dashboard\_read\_repository.py` | Tidak aktif di production execution path |

# | FR-004 | `DashboardProjection` | `backend/infrastructure/projections/dashboard\_projection.py` | Tidak aktif di production execution path |

# | FR-005 | `WorkflowService` | `backend/services/workflow\_service.py` | Tidak aktif di production execution path |

# 

# \#### Type B — Architectural Preservation

# 

# | ID | Komponen | File | ADR Reference |

# | :--- | :--- | :--- | :--- |

# | FR-006 | `ProjectionRebuilder` | `backend/infrastructure/projections/rebuild.py` | ADR-027 |

# | FR-007 | `ProjectionCheckpoint` | `backend/infrastructure/models/projection\_checkpoint.py` | ADR-027 |

# | FR-008 | `OutboxPublisher` | `backend/infrastructure/outbox/publisher.py` | ADR-020 |

# | FR-009 | `AnalyzeCaseCommandHandler` | `backend/application/commands/analysis\_mapper.py` | ADR-020 |

# 

# \### 3.7. Komponen yang Tetap Aktif (Active)

# 

# | Komponen | Alasan |

# | :--- | :--- |

# | `EventStore` | Digunakan oleh `EvidenceService`, `ReplayEngine`, `TemporalEngine`, dan endpoint `/events` |

# | `events` table | Fondasi data untuk event sourcing. \*\*Data produksi bergantung padanya.\*\* |

# | `snapshots` table | Fondasi data untuk snapshot. \*\*Data produksi bergantung padanya.\*\* |

# | `RiskApplicationService` | Production execution path |

# | `RiskProjectionService` | Production execution path |

# | `ReplayEngine` | Digunakan oleh fitur replay |

# | `TemporalEngine` | Digunakan oleh fitur temporal analysis |

# | `GraphProjectionService` | Digunakan oleh `GraphRegenerationService` |

# 

# \---

# 

# \## 4. Documentation

# 

# \### 4.1. Komentar di File

# 

# ```python

# \# ============================================================================

# \# FROZEN COMPONENT — ADR-030

# \#

# \# Status : Frozen Architectural Asset

# \# Freeze ID : FR-XXX

# \# Type : Dormant Runtime / Architectural Preservation

# \# Architecture Owner : Architecture Team

# \#

# \# DO NOT DELETE — This component is an intentionally preserved architectural asset.

# \#

# \# Functional Behavior : MUST remain unchanged.

# \# Allowed Modifications : Security patches, compatibility updates, type hints,

# \#                         documentation, build-system changes.

# \# Prohibited Modifications : New features, refactoring, redesign, API changes,

# \#                            behavior changes.

# \#

# \# See ADR-030 for details.

# \# Review Date : Sprint 19 (every 2 sprints)

# \# ============================================================================

