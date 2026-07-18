"""
Status Mapper — EngineStatus → Legacy Status.

ARCHITECTURE:
- Mapper adalah komponen terpisah, bukan bagian dari Presenter
- HANYA mapping EngineStatus ke string legacy
- TIDAK ada business logic di sini
- Mudah diubah bila rule mapping berubah
- Dapat di-test secara independen

ADR-020: Presenter = Serializer
Mapper = Transformer (bukan business logic)
"""

from backend.domain.enums import EngineStatus


class StatusMapper:
    """Map EngineStatus to legacy status strings."""
    
    # ===== Legacy Mapping =====
    _LEGACY_MAP = {
        EngineStatus.OK: "SUCCESS",
        EngineStatus.FAILED: "FAILED",
        EngineStatus.PARTIAL: "PARTIAL",
        EngineStatus.SKIPPED: "UNKNOWN",
    }
    
    @classmethod
    def to_legacy(cls, status: EngineStatus) -> str:
        """Convert EngineStatus to legacy status string."""
        return cls._LEGACY_MAP.get(status, "UNKNOWN")
    
    @classmethod
    def to_legacy_batch(cls, statuses: list[EngineStatus]) -> list[str]:
        """Convert multiple EngineStatus to legacy status strings."""
        return [cls.to_legacy(s) for s in statuses]