"""
NEMESIS Madina - Confidence Policy
Pure function - returns 0..1
"""

from typing import Optional

from backend.domain.value_objects.confidence_weights import ConfidenceWeights
from backend.domain.value_objects.confidence_components import ConfidenceComponents


def calculate_confidence(
    components: ConfidenceComponents,
    weights: Optional[ConfidenceWeights] = None,
) -> float:
    """
    Calculate overall confidence from components.
    ✅ Returns 0..1 (domain range)
    ✅ Presentation layer multiplies by 100
    """
    if weights is None:
        weights = ConfidenceWeights.default()
    
    total = (
        weights.fraud * components.fraud +
        weights.evidence * components.evidence +
        weights.graph * components.graph +
        weights.procurement * components.procurement
    )
    return min(1.0, max(0.0, total))