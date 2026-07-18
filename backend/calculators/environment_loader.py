"""
Environment Loader for CalculatorConfig.
"""

import os
from typing import Dict, Any
import logging

from backend.calculators.config import (
    CalculatorConfig,
    FraudWeights,
    RiskWeights,
    EvidenceWeights,
    GraphWeights,  # ← TAMBAHKAN
)

logger = logging.getLogger(__name__)


class EnvironmentCalculatorLoader:
    """
    Load CalculatorConfig from environment variables.

    Separates configuration loading from CalculatorConfig class.
    """

    @staticmethod
    def _get_float(name: str, default: float) -> float:
        """Get float from environment with validation (0-1 range)."""
        value_str = os.getenv(name, str(default))
        try:
            value = float(value_str)
            if value < 0 or value > 1:
                raise ValueError(f"{name}={value} must be between 0 and 1")
            return value
        except ValueError as e:
            raise ValueError(f"Invalid {name}='{value_str}': {e}")

    @staticmethod
    def _get_positive_float(name: str, default: float) -> float:
        """Get float from environment (must be > 0)."""
        value_str = os.getenv(name, str(default))
        try:
            value = float(value_str)
            if value <= 0:
                raise ValueError(f"{name}={value} must be > 0")
            return value
        except ValueError as e:
            raise ValueError(f"Invalid {name}='{value_str}': {e}")

    @classmethod
    def load(cls) -> CalculatorConfig:
        """
        Load CalculatorConfig from environment variables.

        Raises:
            ValueError: If any weight is invalid
        """
        try:
            # ===== 1. Fraud =====
            fraud_weights = FraudWeights(
                severity_weight=cls._get_float("FRAUD_SEVERITY_WEIGHT", 0.40),
                confidence_weight=cls._get_float("FRAUD_CONFIDENCE_WEIGHT", 0.40),
                validated_weight=cls._get_float("FRAUD_VALIDATED_WEIGHT", 0.10),
                variety_weight=cls._get_float("FRAUD_VARIETY_WEIGHT", 0.10)
            ).validate()

            # ===== 2. Risk =====
            risk_weights = RiskWeights(
                anomaly_weight=cls._get_float("RISK_ANOMALY_WEIGHT", 0.30),
                collusion_weight=cls._get_float("RISK_COLLUSION_WEIGHT", 0.30),
                financial_weight=cls._get_float("RISK_FINANCIAL_WEIGHT", 0.25),
                temporal_weight=cls._get_float("RISK_TEMPORAL_WEIGHT", 0.15)
            ).validate()

            # ===== 3. Evidence =====
            evidence_weights = EvidenceWeights(
                trust_weight=cls._get_float("EVIDENCE_TRUST_WEIGHT", 0.40),
                confidence_weight=cls._get_float("EVIDENCE_CONFIDENCE_WEIGHT", 0.35),
                verification_weight=cls._get_float("EVIDENCE_VERIFICATION_WEIGHT", 0.25)
            ).validate()

            # ===== 4. Graph (TAMBAHKAN) =====
            graph_weights = GraphWeights(
                entity_weight=cls._get_float("GRAPH_ENTITY_WEIGHT", 0.40),
                relationship_weight=cls._get_float("GRAPH_RELATIONSHIP_WEIGHT", 0.60),
                entity_scale=cls._get_positive_float("GRAPH_ENTITY_SCALE", 0.05),
                density_scale=cls._get_positive_float("GRAPH_DENSITY_SCALE", 10.0),
                max_entity_score=cls._get_positive_float("GRAPH_MAX_ENTITY_SCORE", 100.0),
                max_relationship_score=cls._get_positive_float("GRAPH_MAX_RELATIONSHIP_SCORE", 100.0),
            ).validate()

            # ===== 5. Build Config =====
            config = CalculatorConfig()
            config.register_fraud(fraud_weights)
            config.register_risk(risk_weights)
            config.register_evidence(evidence_weights)
            config.register_graph(graph_weights)  # ← TAMBAHKAN
            config.freeze()

            return config

        except ValueError as e:
            raise ValueError(f"CalculatorConfig validation failed: {e}")