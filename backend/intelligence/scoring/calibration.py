"""
Scoring Configuration & Calibration
"""
from typing import Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)


class CaseType(str, Enum):
    PROCUREMENT = "procurement"
    VILLAGE_FUND = "village_fund"
    BUDGET = "budget"
    INVESTIGATION = "investigation"
    GENERAL = "general"


@dataclass
class ScoringConfig:
    case_type: CaseType
    weights: Dict[str, float]
    thresholds: Dict[str, float]
    rules_enabled: List[str]
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "case_type": self.case_type.value,
            "weights": self.weights,
            "thresholds": self.thresholds,
            "rules_enabled": self.rules_enabled,
            "description": self.description
        }


class ScoringConfigManager:
    def __init__(self):
        self.configs: Dict[str, ScoringConfig] = {}
        self._init_default_configs()

    def _init_default_configs(self):
        # Procurement
        self.configs[CaseType.PROCUREMENT.value] = ScoringConfig(
            case_type=CaseType.PROCUREMENT,
            weights={"fraud_score": 0.40, "graph_risk": 0.25, "history_score": 0.20, "evidence_trust": 0.15},
            thresholds={"high_risk": 70, "medium_risk": 40, "low_risk": 20},
            rules_enabled=["tender_split", "vendor_concentration", "abnormal_price"],
            description="Scoring for procurement cases"
        )

        # Village Fund
        self.configs[CaseType.VILLAGE_FUND.value] = ScoringConfig(
            case_type=CaseType.VILLAGE_FUND,
            weights={"fraud_score": 0.35, "graph_risk": 0.20, "history_score": 0.25, "evidence_trust": 0.20},
            thresholds={"high_risk": 65, "medium_risk": 35, "low_risk": 20},
            rules_enabled=["fund_misuse", "reporting_delay"],
            description="Scoring for village fund cases"
        )

        # Budget
        self.configs[CaseType.BUDGET.value] = ScoringConfig(
            case_type=CaseType.BUDGET,
            weights={"fraud_score": 0.30, "graph_risk": 0.20, "history_score": 0.20, "evidence_trust": 0.30},
            thresholds={"high_risk": 60, "medium_risk": 35, "low_risk": 15},
            rules_enabled=["budget_variance", "unapproved_spending"],
            description="Scoring for budget cases"
        )

        # Investigation
        self.configs[CaseType.INVESTIGATION.value] = ScoringConfig(
            case_type=CaseType.INVESTIGATION,
            weights={"fraud_score": 0.25, "graph_risk": 0.30, "history_score": 0.20, "evidence_trust": 0.25},
            thresholds={"high_risk": 75, "medium_risk": 45, "low_risk": 25},
            rules_enabled=["witness_credibility", "document_authenticity"],
            description="Scoring for investigation cases"
        )

        # General
        self.configs[CaseType.GENERAL.value] = ScoringConfig(
            case_type=CaseType.GENERAL,
            weights={"fraud_score": 0.30, "graph_risk": 0.25, "history_score": 0.20, "evidence_trust": 0.25},
            thresholds={"high_risk": 70, "medium_risk": 40, "low_risk": 20},
            rules_enabled=["general_fraud_indicator", "unusual_pattern"],
            description="General scoring configuration"
        )

    def get_config(self, case_type: CaseType) -> ScoringConfig:
        return self.configs.get(case_type.value, self.configs[CaseType.GENERAL.value])

    def update_config(self, config: ScoringConfig) -> None:
        self.configs[config.case_type.value] = config
        logger.info(f"Scoring config updated for: {config.case_type.value}")

    def get_all_configs(self) -> Dict[str, Dict[str, Any]]:
        return {key: config.to_dict() for key, config in self.configs.items()}

    def export_configs(self) -> str:
        return json.dumps(self.get_all_configs(), indent=2)


scoring_config_manager = ScoringConfigManager()
