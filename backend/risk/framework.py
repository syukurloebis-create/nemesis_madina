# backend/risk/framework.py
from enum import Enum
from typing import Optional, List, Dict, Any, Callable
from datetime import datetime
from dataclasses import dataclass, field
import uuid


class RiskLevel(str, Enum):
    """Level risiko"""
    LOW = "LOW"           # 0-25 - Risiko rendah
    MEDIUM = "MEDIUM"     # 26-50 - Risiko sedang
    HIGH = "HIGH"         # 51-75 - Risiko tinggi
    CRITICAL = "CRITICAL" # 76-100 - Risiko kritis


class RiskCategory(str, Enum):
    """Kategori risiko"""
    PROCUREMENT = "PROCUREMENT"           # Risiko pengadaan
    FINANCIAL = "FINANCIAL"               # Risiko keuangan
    GOVERNANCE = "GOVERNANCE"             # Risiko tata kelola
    COMPLIANCE = "COMPLIANCE"             # Risiko kepatuhan
    REPUTATION = "REPUTATION"             # Risiko reputasi
    LEGAL = "LEGAL"                       # Risiko hukum
    OPERATIONAL = "OPERATIONAL"           # Risiko operasional


class RiskTargetType(str, Enum):
    """Target penilaian risiko"""
    CASE = "CASE"
    ENTITY = "ENTITY"
    VENDOR = "VENDOR"
    OFFICIAL = "OFFICIAL"
    OPD = "OPD"
    DISTRICT = "DISTRICT"


@dataclass
class RiskFactor:
    """Faktor risiko"""
    factor_id: str
    name: str
    description: str
    category: RiskCategory
    weight: float  # 0-1, sum of all weights should be 1
    min_score: float = 0
    max_score: float = 100
    default_score: float = 0
    calculation_method: str = "MANUAL"  # MANUAL, FORMULA, AI
    
    def calculate_score(self, data: Dict[str, Any]) -> float:
        """Calculate score based on data"""
        # Override in subclass
        return self.default_score


@dataclass
class RiskAssessmentRule:
    """Rule untuk penilaian risiko"""
    rule_id: str
    name: str
    description: str
    factor_id: str
    condition: str  # Expression to evaluate
    score: float
    priority: int = 0


@dataclass
class RiskAssessmentResult:
    """Hasil penilaian risiko"""
    assessment_id: uuid.UUID
    target_type: RiskTargetType
    target_id: uuid.UUID
    timestamp: datetime
    total_score: float
    risk_level: RiskLevel
    factor_scores: Dict[str, float]
    factor_details: Dict[str, Any]
    recommendations: List[str]
    model_version: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "assessment_id": str(self.assessment_id),
            "target_type": self.target_type.value,
            "target_id": str(self.target_id),
            "timestamp": self.timestamp.isoformat(),
            "total_score": self.total_score,
            "risk_level": self.risk_level.value,
            "factor_scores": self.factor_scores,
            "factor_details": self.factor_details,
            "recommendations": self.recommendations,
            "model_version": self.model_version
        }


class RiskGovernanceFramework:
    """Framework untuk governance risiko"""
    
    def __init__(self):
        self._factors: Dict[str, RiskFactor] = {}
        self._rules: Dict[str, RiskAssessmentRule] = {}
        self._thresholds: Dict[RiskLevel, tuple] = {
            RiskLevel.LOW: (0, 25),
            RiskLevel.MEDIUM: (26, 50),
            RiskLevel.HIGH: (51, 75),
            RiskLevel.CRITICAL: (76, 100)
        }
        self._init_framework()
    
    def _init_framework(self):
        """Initialize risk framework with default factors"""
        
        # Procurement risk factors
        self._factors["vendor_dominance"] = RiskFactor(
            factor_id="vendor_dominance",
            name="Vendor Dominance",
            description="Tingkat dominasi vendor dalam pengadaan",
            category=RiskCategory.PROCUREMENT,
            weight=0.15,
            calculation_method="FORMULA"
        )
        
        self._factors["bid_rotation"] = RiskFactor(
            factor_id="bid_rotation",
            name="Bid Rotation",
            description="Pola rotasi pemenang tender",
            category=RiskCategory.PROCUREMENT,
            weight=0.12,
            calculation_method="FORMULA"
        )
        
        self._factors["single_bidder"] = RiskFactor(
            factor_id="single_bidder",
            name="Single Bidder",
            description="Tender dengan peserta tunggal",
            category=RiskCategory.PROCUREMENT,
            weight=0.10,
            calculation_method="FORMULA"
        )
        
        self._factors["price_markup"] = RiskFactor(
            factor_id="price_markup",
            name="Price Markup",
            description="Kelebihan harga dari wajar",
            category=RiskCategory.FINANCIAL,
            weight=0.12,
            calculation_method="FORMULA"
        )
        
        # Governance risk factors
        self._factors["conflict_of_interest"] = RiskFactor(
            factor_id="conflict_of_interest",
            name="Conflict of Interest",
            description="Potensi benturan kepentingan",
            category=RiskCategory.GOVERNANCE,
            weight=0.15,
            calculation_method="FORMULA"
        )
        
        self._factors["family_connection"] = RiskFactor(
            factor_id="family_connection",
            name="Family Connection",
            description="Hubungan keluarga antar entitas",
            category=RiskCategory.GOVERNANCE,
            weight=0.08,
            calculation_method="FORMULA"
        )
        
        # Compliance risk factors
        self._factors["regulatory_violation"] = RiskFactor(
            factor_id="regulatory_violation",
            name="Regulatory Violation",
            description="Pelanggaran regulasi",
            category=RiskCategory.COMPLIANCE,
            weight=0.10,
            calculation_method="FORMULA"
        )
        
        self._factors["document_irregularity"] = RiskFactor(
            factor_id="document_irregularity",
            name="Document Irregularity",
            description="Kejanggalan dokumen",
            category=RiskCategory.COMPLIANCE,
            weight=0.08,
            calculation_method="FORMULA"
        )
        
        # Network risk factors
        self._factors["collusion_network"] = RiskFactor(
            factor_id="collusion_network",
            name="Collusion Network",
            description="Keterlibatan dalam jaringan kolusi",
            category=RiskCategory.GOVERNANCE,
            weight=0.10,
            calculation_method="FORMULA"
        )
        
        # Register rules
        self._init_rules()
    
    def _init_rules(self):
        """Initialize risk assessment rules"""
        
        # Vendor dominance rules
        self._rules["vendor_dominance_high"] = RiskAssessmentRule(
            rule_id="vendor_dominance_high",
            name="High Vendor Dominance",
            description="Vendor mendominasi lebih dari 30% paket",
            factor_id="vendor_dominance",
            condition="package_share > 0.3",
            score=100,
            priority=1
        )
        
        self._rules["vendor_dominance_medium"] = RiskAssessmentRule(
            rule_id="vendor_dominance_medium",
            name="Medium Vendor Dominance",
            description="Vendor mendominasi 15-30% paket",
            factor_id="vendor_dominance",
            condition="0.15 < package_share <= 0.3",
            score=60,
            priority=2
        )
        
        self._rules["vendor_dominance_low"] = RiskAssessmentRule(
            rule_id="vendor_dominance_low",
            name="Low Vendor Dominance",
            description="Vendor mendominasi kurang dari 15% paket",
            factor_id="vendor_dominance",
            condition="package_share <= 0.15",
            score=20,
            priority=3
        )
        
        # Single bidder rules
        self._rules["single_bidder_high"] = RiskAssessmentRule(
            rule_id="single_bidder_high",
            name="High Single Bidder Rate",
            description="Lebih dari 50% tender hanya satu peserta",
            factor_id="single_bidder",
            condition="single_bidder_rate > 0.5",
            score=100,
            priority=1
        )
        
        self._rules["single_bidder_medium"] = RiskAssessmentRule(
            rule_id="single_bidder_medium",
            name="Medium Single Bidder Rate",
            description="25-50% tender hanya satu peserta",
            factor_id="single_bidder",
            condition="0.25 <= single_bidder_rate <= 0.5",
            score=60,
            priority=2
        )
        
        # Conflict of interest rules
        self._rules["coi_direct"] = RiskAssessmentRule(
            rule_id="coi_direct",
            name="Direct Conflict of Interest",
            description="Hubungan langsung antara pejabat dan vendor",
            factor_id="conflict_of_interest",
            condition="has_direct_relationship = True",
            score=100,
            priority=1
        )
        
        self._rules["coi_indirect"] = RiskAssessmentRule(
            rule_id="coi_indirect",
            name="Indirect Conflict of Interest",
            description="Hubungan tidak langsung (keluarga, saham)",
            factor_id="conflict_of_interest",
            condition="has_indirect_relationship = True",
            score=70,
            priority=2
        )
        
        # Collusion network rules
        self._rules["collusion_central"] = RiskAssessmentRule(
            rule_id="collusion_central",
            name="Central in Collusion Network",
            description="Entitas sentral dalam jaringan kolusi",
            factor_id="collusion_network",
            condition="network_centrality > 0.7",
            score=100,
            priority=1
        )
        
        self._rules["collusion_peripheral"] = RiskAssessmentRule(
            rule_id="collusion_peripheral",
            name="Peripheral in Collusion Network",
            description="Entitas di pinggiran jaringan kolusi",
            factor_id="collusion_network",
            condition="0.3 < network_centrality <= 0.7",
            score=60,
            priority=2
        )
    
    def get_factor(self, factor_id: str) -> Optional[RiskFactor]:
        """Get risk factor by ID"""
        return self._factors.get(factor_id)
    
    def get_all_factors(self) -> List[RiskFactor]:
        """Get all risk factors"""
        return list(self._factors.values())
    
    def get_factors_by_category(self, category: RiskCategory) -> List[RiskFactor]:
        """Get risk factors by category"""
        return [f for f in self._factors.values() if f.category == category]
    
    def get_rules_for_factor(self, factor_id: str) -> List[RiskAssessmentRule]:
        """Get all rules for a factor"""
        return [r for r in self._rules.values() if r.factor_id == factor_id]
    
    def get_risk_level(self, score: float) -> RiskLevel:
        """Determine risk level based on score"""
        for level, (min_score, max_score) in self._thresholds.items():
            if min_score <= score <= max_score:
                return level
        return RiskLevel.MEDIUM
    
    def get_threshold(self, level: RiskLevel) -> tuple:
        """Get threshold for risk level"""
        return self._thresholds.get(level, (0, 100))
    
    def get_weight_sum(self) -> float:
        """Get sum of all factor weights (should be 1.0)"""
        return sum(f.weight for f in self._factors.values())
    
    def validate_weights(self) -> bool:
        """Validate that total weight equals 1.0"""
        total = self.get_weight_sum()
        return abs(total - 1.0) < 0.01
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert framework to dictionary"""
        return {
            "factors": [
                {
                    "factor_id": f.factor_id,
                    "name": f.name,
                    "description": f.description,
                    "category": f.category.value,
                    "weight": f.weight,
                    "calculation_method": f.calculation_method
                }
                for f in self._factors.values()
            ],
            "thresholds": {
                level.value: {"min": min_val, "max": max_val}
                for level, (min_val, max_val) in self._thresholds.items()
            },
            "total_weight": self.get_weight_sum(),
            "weights_valid": self.validate_weights()
        }


# Singleton instance
_risk_framework = None

def get_risk_framework() -> RiskGovernanceFramework:
    """Get singleton risk framework"""
    global _risk_framework
    if _risk_framework is None:
        _risk_framework = RiskGovernanceFramework()
    return _risk_framework