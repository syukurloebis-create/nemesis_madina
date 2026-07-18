"""
Procurement Risk
Analisis risiko procurement
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class ProcurementRiskResult:
    """Hasil analisis risiko procurement"""
    procurement_id: str
    overall_risk: float
    components: Dict[str, float]
    anomalies: List[Dict[str, Any]]
    recommendations: List[str]
    confidence: float
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "procurement_id": self.procurement_id,
            "overall_risk": self.overall_risk,
            "components": self.components,
            "anomalies": self.anomalies,
            "recommendations": self.recommendations,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat()
        }


class ProcurementRiskAnalyzer:
    """
    Procurement Risk Analysis
    Menganalisis risiko dalam procurement
    """

    def __init__(self):
        self.thresholds = {
            "price_anomaly": 0.3,  # 30% deviation
            "vendor_concentration": 0.5,  # 50% concentration
            "tender_split": 0.4,  # 40% split
            "historical_fraud": 0.3,  # 30% historical fraud
            "document_completeness": 0.7,  # 70% completeness
        }

    def analyze(self, procurement_data: Dict[str, Any]) -> ProcurementRiskResult:
        """
        Analyze procurement risk
        """
        components = {}

        # 1. Price anomaly
        price_risk = self._analyze_price_anomaly(procurement_data)
        components["price_risk"] = price_risk

        # 2. Vendor concentration
        vendor_risk = self._analyze_vendor_concentration(procurement_data)
        components["vendor_risk"] = vendor_risk

        # 3. Tender split
        split_risk = self._analyze_tender_split(procurement_data)
        components["split_risk"] = split_risk

        # 4. Historical fraud
        historical_risk = self._analyze_historical_fraud(procurement_data)
        components["historical_risk"] = historical_risk

        # 5. Document completeness
        document_risk = self._analyze_document_completeness(procurement_data)
        components["document_risk"] = document_risk

        # Calculate overall risk
        weights = {
            "price_risk": 0.25,
            "vendor_risk": 0.20,
            "split_risk": 0.20,
            "historical_risk": 0.20,
            "document_risk": 0.15
        }

        overall = sum(components[k] * weights[k] for k in components)

        # Detect anomalies
        anomalies = self._detect_anomalies(procurement_data, components)

        # Generate recommendations
        recommendations = self._generate_recommendations(components, anomalies)

        return ProcurementRiskResult(
            procurement_id=procurement_data.get("id", "unknown"),
            overall_risk=overall,
            components=components,
            anomalies=anomalies,
            recommendations=recommendations,
            confidence=0.85
        )

    def _analyze_price_anomaly(self, data: Dict[str, Any]) -> float:
        """Analyze price anomaly"""
        expected_price = data.get("expected_price", 0)
        actual_price = data.get("actual_price", 0)

        if expected_price == 0:
            return 0

        deviation = abs(actual_price - expected_price) / expected_price
        return min(deviation / self.thresholds["price_anomaly"], 1.0) * 100

    def _analyze_vendor_concentration(self, data: Dict[str, Any]) -> float:
        """Analyze vendor concentration"""
        total_vendors = data.get("total_vendors", 0)
        unique_vendors = data.get("unique_vendors", 0)

        if total_vendors == 0:
            return 0

        concentration = 1 - (unique_vendors / total_vendors)
        return min(concentration / self.thresholds["vendor_concentration"], 1.0) * 100

    def _analyze_tender_split(self, data: Dict[str, Any]) -> float:
        """Analyze tender split"""
        total_value = data.get("total_value", 0)
        packages = data.get("packages", [])

        if not packages or total_value == 0:
            return 0

        # Check if packages are unusually small
        avg_package = total_value / len(packages)
        small_packages = [p for p in packages if p.get("value", 0) < avg_package * 0.3]

        split_ratio = len(small_packages) / len(packages) if packages else 0
        return min(split_ratio / self.thresholds["tender_split"], 1.0) * 100

    def _analyze_historical_fraud(self, data: Dict[str, Any]) -> float:
        """Analyze historical fraud"""
        fraud_cases = data.get("fraud_cases", 0)
        total_cases = data.get("total_cases", 1)

        fraud_rate = fraud_cases / total_cases if total_cases > 0 else 0
        return min(fraud_rate / self.thresholds["historical_fraud"], 1.0) * 100

    def _analyze_document_completeness(self, data: Dict[str, Any]) -> float:
        """Analyze document completeness"""
        required_docs = data.get("required_documents", [])
        provided_docs = data.get("provided_documents", [])

        if not required_docs:
            return 0

        completeness = len(provided_docs) / len(required_docs)
        return (1 - min(completeness / self.thresholds["document_completeness"], 1.0)) * 100

    def _detect_anomalies(
        self,
        data: Dict[str, Any],
        components: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Detect anomalies in procurement"""
        anomalies = []

        if components.get("price_risk", 0) > 70:
            anomalies.append({
                "type": "price_anomaly",
                "severity": "HIGH",
                "description": f"Price deviation detected: {data.get('expected_price', 0)} vs {data.get('actual_price', 0)}",
                "recommendation": "Verify pricing with market comparison"
            })

        if components.get("vendor_risk", 0) > 70:
            anomalies.append({
                "type": "vendor_concentration",
                "severity": "HIGH",
                "description": f"High vendor concentration: {data.get('unique_vendors', 0)} vendors for {data.get('total_vendors', 0)} transactions",
                "recommendation": "Diversify vendor base"
            })

        if components.get("split_risk", 0) > 70:
            anomalies.append({
                "type": "tender_split",
                "severity": "MEDIUM",
                "description": f"Suspicious tender split detected",
                "recommendation": "Review package breakdown"
            })

        return anomalies

    def _generate_recommendations(
        self,
        components: Dict[str, float],
        anomalies: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []

        if components.get("price_risk", 0) > 60:
            recommendations.append("Conduct market price comparison")

        if components.get("vendor_risk", 0) > 60:
            recommendations.append("Review vendor selection process")

        if components.get("split_risk", 0) > 60:
            recommendations.append("Analyze tender split justification")

        if components.get("historical_risk", 0) > 60:
            recommendations.append("Review historical fraud patterns")

        if components.get("document_risk", 0) > 60:
            recommendations.append("Complete missing documentation")

        for anomaly in anomalies:
            if anomaly.get("recommendation"):
                recommendations.append(anomaly["recommendation"])

        return list(set(recommendations))


# Singleton instance
procurement_risk_analyzer = ProcurementRiskAnalyzer()