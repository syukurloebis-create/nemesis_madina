from dataclasses import dataclass
from typing import Any, List


@dataclass
class FeatureContribution:
    feature: str
    value: Any
    contribution: float
    description: str


@dataclass
class ExplanationResult:
    risk_score: float
    confidence_score: float
    top_factors: List[FeatureContribution]
    summary: str