"""
Feature Store
Definisi dan kalkulasi feature untuk intelligence
"""
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class FeatureType(str, Enum):
    """Tipe feature"""
    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    STRING = "string"
    ARRAY = "array"


class FeatureSource(str, Enum):
    """Sumber feature"""
    CASE = "case"
    EVIDENCE = "evidence"
    GRAPH = "graph"
    FRAUD = "fraud"
    PROCUREMENT = "procurement"
    COMPOSITE = "composite"


@dataclass
class FeatureDefinition:
    """Definisi feature"""
    name: str
    description: str
    feature_type: FeatureType
    source: FeatureSource
    calculation: str
    validation: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    version: int = 1
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class FeatureStore:
    """Store untuk feature definitions dan calculations"""

    def __init__(self):
        self.definitions: Dict[str, FeatureDefinition] = {}
        self.calculators: Dict[str, Callable] = {}
        self._init_default_features()

    def _init_default_features(self) -> None:
        """Initialize default features"""
        default_features = [
            FeatureDefinition(
                name="case_risk_score",
                description="Risk score dari case",
                feature_type=FeatureType.NUMERIC,
                source=FeatureSource.CASE,
                calculation="SELECT risk_score FROM cases WHERE id = :case_id"
            ),
            FeatureDefinition(
                name="evidence_count",
                description="Jumlah evidence dalam case",
                feature_type=FeatureType.NUMERIC,
                source=FeatureSource.EVIDENCE,
                calculation="SELECT COUNT(*) FROM evidence WHERE case_id = :case_id"
            ),
            FeatureDefinition(
                name="evidence_trust_avg",
                description="Rata-rata trust score evidence",
                feature_type=FeatureType.NUMERIC,
                source=FeatureSource.EVIDENCE,
                calculation="SELECT AVG(trust_score) FROM evidence WHERE case_id = :case_id"
            ),
            FeatureDefinition(
                name="graph_degree",
                description="Degree entity dalam graph",
                feature_type=FeatureType.NUMERIC,
                source=FeatureSource.GRAPH,
                calculation="SELECT degree FROM graph_entities WHERE id = :entity_id"
            ),
            FeatureDefinition(
                name="fraud_pattern_count",
                description="Jumlah fraud pattern dalam case",
                feature_type=FeatureType.NUMERIC,
                source=FeatureSource.FRAUD,
                calculation="SELECT COUNT(*) FROM fraud_patterns WHERE case_id = :case_id"
            ),
            FeatureDefinition(
                name="procurement_anomaly_count",
                description="Jumlah anomaly dalam procurement",
                feature_type=FeatureType.NUMERIC,
                source=FeatureSource.PROCUREMENT,
                calculation="SELECT COUNT(*) FROM procurement_anomalies WHERE case_id = :case_id"
            ),
            FeatureDefinition(
                name="has_collusion",
                description="Apakah ada indikasi collusion",
                feature_type=FeatureType.BOOLEAN,
                source=FeatureSource.GRAPH,
                calculation="SELECT EXISTS(SELECT 1 FROM collusion_detections WHERE case_id = :case_id)"
            ),
            FeatureDefinition(
                name="total_evidence",
                description="Total evidence dalam case",
                feature_type=FeatureType.NUMERIC,
                source=FeatureSource.COMPOSITE,
                calculation="evidence_count",
                dependencies=["evidence_count"]
            ),
        ]

        for feature in default_features:
            self.register_feature(feature)

    def register_feature(self, definition: FeatureDefinition) -> None:
        """Register feature definition"""
        self.definitions[definition.name] = definition
        logger.info(f"Feature registered: {definition.name}")

    def register_calculator(self, feature_name: str, calculator: Callable) -> None:
        """Register calculator function for a feature"""
        if feature_name not in self.definitions:
            raise ValueError(f"Feature {feature_name} not defined")
        self.calculators[feature_name] = calculator
        logger.info(f"Calculator registered for: {feature_name}")

    def get_definition(self, feature_name: str) -> Optional[FeatureDefinition]:
        """Get feature definition"""
        return self.definitions.get(feature_name)

    def get_all_definitions(self) -> List[FeatureDefinition]:
        """Get all feature definitions"""
        return list(self.definitions.values())

    def get_definitions_by_source(self, source: FeatureSource) -> List[FeatureDefinition]:
        """Get definitions by source"""
        return [f for f in self.definitions.values() if f.source == source]

    def calculate_feature(self, feature_name: str, context: Dict[str, Any]) -> Any:
        """Calculate feature value"""
        if feature_name not in self.definitions:
            raise ValueError(f"Feature {feature_name} not defined")

        if feature_name in self.calculators:
            return self.calculators[feature_name](context)

        # Default calculation based on definition
        definition = self.definitions[feature_name]
        if definition.calculation:
            # Placeholder: implement query execution
            logger.warning(f"Calculator not registered for {feature_name}, using placeholder")
            return None

        return None

    def calculate_features(
        self,
        feature_names: List[str],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate multiple features"""
        results = {}
        for name in feature_names:
            try:
                results[name] = self.calculate_feature(name, context)
            except Exception as e:
                logger.error(f"Failed to calculate {name}: {e}")
                results[name] = None
        return results


# Singleton instance
feature_store = FeatureStore()