"""
Calculators Assembler — Create all calculators.
"""

from backend.calculators.fraud_score_calculator import FraudScoreCalculator
from backend.calculators.risk_score_calculator import RiskScoreCalculator
from backend.calculators.evidence_score_calculator import EvidenceScoreCalculator
from backend.calculators.config import CalculatorConfig


def create_calculators(config: CalculatorConfig):
    """Create all calculators."""
    return {
        "fraud": FraudScoreCalculator(),
        "risk": RiskScoreCalculator(),
        "evidence": EvidenceScoreCalculator(),
        "config": config
    }