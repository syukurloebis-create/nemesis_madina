"""
Exception classification untuk logging yang lebih baik.
"""

from typing import Type, Dict


class IntelligenceException(Exception):
    """Base exception untuk intelligence module."""
    pass


class FraudEngineError(IntelligenceException):
    """Error dari Fraud Engine."""
    pass


class GraphEngineError(IntelligenceException):
    """Error dari Graph Engine."""
    pass


class RiskEngineError(IntelligenceException):
    """Error dari Risk Engine."""
    pass


class EvidenceEngineError(IntelligenceException):
    """Error dari Evidence Engine."""
    pass


class FindingGenerationError(IntelligenceException):
    """Error saat generate findings."""
    pass


class LifecycleError(IntelligenceException):
    """Error di lifecycle service."""
    pass


class CacheError(IntelligenceException):
    """Error di cache layer."""
    pass


# Mapping error types untuk logging
ERROR_TYPE_MAP: Dict[Type[Exception], str] = {
    FraudEngineError: "FRAUD_ENGINE",
    GraphEngineError: "GRAPH_ENGINE",
    RiskEngineError: "RISK_ENGINE",
    EvidenceEngineError: "EVIDENCE_ENGINE",
    FindingGenerationError: "FINDING_GENERATION",
    LifecycleError: "LIFECYCLE",
    CacheError: "CACHE",
}