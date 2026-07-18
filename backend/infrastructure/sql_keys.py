"""
SQL Keys — Final, digunakan sebagai kontrak.

All SQL queries are identified by these keys.
"""

from enum import Enum
from typing import Tuple


class SQLKey(Enum):
    """SQL Key — Category dan Query Name."""
    
    # Fraud
    FRAUD_SUMMARY = ("fraud", "summary")
    FRAUD_PATTERNS = ("fraud", "patterns")
    
    # Graph
    GRAPH_SUMMARY = ("graph", "summary")
    
    # Risk
    RISK_SUMMARY = ("risk", "summary")
    
    # Evidence
    EVIDENCE_SUMMARY = ("evidence", "summary")
    
    # Procurement
    PROCUREMENT_SUMMARY = ("procurement", "summary")
    
    @property
    def category(self) -> str:
        return self.value[0]
    
    @property
    def query(self) -> str:
        return self.value[1]
    
    def to_tuple(self) -> Tuple[str, str]:
        return self.value