from dataclasses import dataclass


@dataclass(frozen=True)
class GraphSummaryRow:
    """Graph Summary Row Object — Typed, bukan dict."""
    entities: int = 0
    relationships: int = 0
    
    @classmethod
    def empty(cls) -> "GraphSummaryRow":
        return cls()