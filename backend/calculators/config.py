"""
Calculator Config — Generic, Registry-based.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Optional
from threading import Lock
import os  


# ============================================================================
# 1. WEIGHT CLASSES (Data Only)
# ============================================================================

@dataclass(frozen=True)
class FraudWeights:
    severity_weight: float = 0.40
    confidence_weight: float = 0.40
    validated_weight: float = 0.10
    variety_weight: float = 0.10

    def validate(self) -> "FraudWeights":
        total = self.severity_weight + self.confidence_weight + self.validated_weight + self.variety_weight
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Fraud weights must sum to 1.0, got {total}")
        return self


@dataclass(frozen=True)
class RiskWeights:
    anomaly_weight: float = 0.30
    collusion_weight: float = 0.30
    financial_weight: float = 0.25
    temporal_weight: float = 0.15

    def validate(self) -> "RiskWeights":
        total = self.anomaly_weight + self.collusion_weight + self.financial_weight + self.temporal_weight
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Risk weights must sum to 1.0, got {total}")
        return self


@dataclass(frozen=True)
class EvidenceWeights:
    trust_weight: float = 0.40
    confidence_weight: float = 0.35
    verification_weight: float = 0.25

    def validate(self) -> "EvidenceWeights":
        total = self.trust_weight + self.confidence_weight + self.verification_weight
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Evidence weights must sum to 1.0, got {total}")
        return self


@dataclass(frozen=True)
class GraphWeights:
    entity_weight: float = 0.40
    relationship_weight: float = 0.60
    entity_scale: float = 0.05
    density_scale: float = 10.0
    max_entity_score: float = 100.0
    max_relationship_score: float = 100.0

    def validate(self) -> "GraphWeights":
        total = self.entity_weight + self.relationship_weight
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Graph weights must sum to 1.0, got {total}")
        if self.entity_scale <= 0:
            raise ValueError("entity_scale must be > 0")
        if self.density_scale <= 0:
            raise ValueError("density_scale must be > 0")
        return self


# ============================================================================
# 2. CALCULATOR CONFIG (Registry-Based)
# ============================================================================

class CalculatorConfig:
    """
    Calculator Config — Generic, Registry-based.

    Characteristics:
    - Generic register(engine_name, weights)
    - Generic get(engine_name)
    - Register new engines without changing class
    - Frozen after initialization
    """

    def __init__(self):
        # ✅ Registry-based (bukan typed fields)
        self._weights: Dict[str, Dict[str, float]] = {}
        self._lock = Lock()
        self._frozen = False

    # ===== Generic Registry =====

    def register(self, name: str, weights: Dict[str, float]) -> "CalculatorConfig":
        """Generic register — untuk semua engine."""
        if self._frozen:
            raise RuntimeError("Config is frozen. Cannot register new weights.")

        with self._lock:
            if self._frozen:
                raise RuntimeError("Config is frozen. Cannot register new weights.")
            self._weights[name] = weights

        return self

    def get(self, name: str) -> Dict[str, float]:
        """Generic get — untuk semua engine."""
        if name not in self._weights:
            raise KeyError(
                f"Calculator config not found: {name}. "
                f"Available: {list(self._weights.keys())}"
            )
        return self._weights[name]

    def list_engines(self) -> list:
        return list(self._weights.keys())

    def is_frozen(self) -> bool:
        return self._frozen

    def freeze(self) -> "CalculatorConfig":
        with self._lock:
            self._frozen = True
        return self

    # ===== Engine-Specific Register =====

    def register_fraud(self, weights: FraudWeights) -> "CalculatorConfig":
        weights.validate()
        return self.register("fraud", {
            "severity_weight": weights.severity_weight,
            "confidence_weight": weights.confidence_weight,
            "validated_weight": weights.validated_weight,
            "variety_weight": weights.variety_weight,
        })

    def register_risk(self, weights: RiskWeights) -> "CalculatorConfig":
        weights.validate()
        return self.register("risk", {
            "anomaly_weight": weights.anomaly_weight,
            "collusion_weight": weights.collusion_weight,
            "financial_weight": weights.financial_weight,
            "temporal_weight": weights.temporal_weight,
        })

    def register_evidence(self, weights: EvidenceWeights) -> "CalculatorConfig":
        weights.validate()
        return self.register("evidence", {
            "trust_weight": weights.trust_weight,
            "confidence_weight": weights.confidence_weight,
            "verification_weight": weights.verification_weight,
        })

    def register_graph(self, weights: GraphWeights) -> "CalculatorConfig":
        weights.validate()
        return self.register("graph", {
            "entity_weight": weights.entity_weight,
            "relationship_weight": weights.relationship_weight,
            "entity_scale": weights.entity_scale,
            "density_scale": weights.density_scale,
            "max_entity_score": weights.max_entity_score,
            "max_relationship_score": weights.max_relationship_score,
        })

    # ===== Engine-Specific Getter =====

    def get_fraud_weights(self) -> FraudWeights:
        w = self.get("fraud")
        return FraudWeights(
            severity_weight=w["severity_weight"],
            confidence_weight=w["confidence_weight"],
            validated_weight=w["validated_weight"],
            variety_weight=w["variety_weight"],
        )

    def get_risk_weights(self) -> RiskWeights:
        w = self.get("risk")
        return RiskWeights(
            anomaly_weight=w["anomaly_weight"],
            collusion_weight=w["collusion_weight"],
            financial_weight=w["financial_weight"],
            temporal_weight=w["temporal_weight"],
        )

    def get_evidence_weights(self) -> EvidenceWeights:
        w = self.get("evidence")
        return EvidenceWeights(
            trust_weight=w["trust_weight"],
            confidence_weight=w["confidence_weight"],
            verification_weight=w["verification_weight"],
        )

    def get_graph_weights(self) -> GraphWeights:
        w = self.get("graph")
        return GraphWeights(
            entity_weight=w["entity_weight"],
            relationship_weight=w["relationship_weight"],
            entity_scale=w["entity_scale"],
            density_scale=w["density_scale"],
            max_entity_score=w["max_entity_score"],
            max_relationship_score=w["max_relationship_score"],
        )

    # ===== Default Configuration =====

    @classmethod
    def default(cls) -> "CalculatorConfig":
        config = cls()
        config.register_fraud(FraudWeights().validate())
        config.register_risk(RiskWeights().validate())
        config.register_evidence(EvidenceWeights().validate())
        config.register_graph(GraphWeights().validate())  # ← TAMBAHKAN
        config.freeze()
        return config

    @classmethod
    def government(cls) -> "CalculatorConfig":
        config = cls()
        config.register_fraud(FraudWeights(
            severity_weight=0.50,
            confidence_weight=0.30,
            validated_weight=0.15,
            variety_weight=0.05,
        ).validate())
        config.register_risk(RiskWeights(
            anomaly_weight=0.35,
            collusion_weight=0.35,
            financial_weight=0.20,
            temporal_weight=0.10,
        ).validate())
        config.register_evidence(EvidenceWeights(
            trust_weight=0.45,
            confidence_weight=0.30,
            verification_weight=0.25,
        ).validate())

        config.register_graph(GraphWeights().validate())
        config.freeze()
        return config

    @classmethod
    def from_environment(cls) -> "CalculatorConfig":
        """
        Build calculator configuration from environment.

        Supported profiles:
            - default
            - government

        Environment:
            CALCULATOR_PROFILE=default|government
        """
        profile = os.getenv(
            "CALCULATOR_PROFILE",
            "default",
        ).strip().lower()

        if profile == "government":
            return cls.government()

        return cls.default()
