from dataclasses import dataclass


@dataclass(frozen=True)
class ProcurementSummaryRow:
    """Procurement Summary Row Object — Typed, bukan dict."""
    packages: int = 0
    vendors: int = 0
    instansi_count: int = 0
    avg_value: float = 0.0
    total_value: float = 0.0
    
    @classmethod
    def empty(cls) -> "ProcurementSummaryRow":
        return cls()