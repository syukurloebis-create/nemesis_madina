from dataclasses import dataclass


@dataclass(frozen=True)
class EvidenceSummaryRow:
    """Evidence Summary Row Object — Typed, bukan dict."""
    total: int = 0
    verified: int = 0
    rejected: int = 0
    pending: int = 0
    avg_trust: float = 0.0
    avg_confidence: float = 0.0
    
    @classmethod
    def empty(cls) -> "EvidenceSummaryRow":
        return cls()