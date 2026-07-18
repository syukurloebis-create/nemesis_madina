"""
Finding Generator - Generate findings from intelligence data
"""

import logging
import uuid
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class FindingGenerator:
    """
    Generate findings from fraud and evidence data.
    """

    # ============================================================
    # ENGINE NAME MAPPING - STANDARISASI
    # ============================================================

    ENGINE_NAME_MAP = {
        "FraudIntelligence": "FraudEngine",
        "GraphIntelligence": "GraphEngine",
        "EvidenceIntelligence": "EvidenceEngine",
        "RiskScorer": "RiskEngine",
        "CollusionEngine": "CollusionEngine",
        "ProcurementEngine": "ProcurementEngine",
    }

    @classmethod
    def _get_engine_name(cls, detection_method: str) -> str:
        """Get standardized engine name."""
        return cls.ENGINE_NAME_MAP.get(detection_method, detection_method)

    @classmethod
    def generate_findings(
        cls,
        case_id: str,
        fraud_data: Dict[str, Any],
        evidence_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate findings from fraud and evidence data.
        """
        findings = []

        # ==============================
        # FRAUD CRITICAL RISK
        # ==============================

        fraud_level = fraud_data.get("overall_risk")
        signals = fraud_data.get("signals", {})
        high_confidence_alerts = fraud_data.get("high_confidence", 0)

        if fraud_level in ["CRITICAL", "HIGH"]:
            # Hitung confidence score berdasarkan level risiko
            if fraud_level == "CRITICAL":
                confidence_score = 95.0
            elif fraud_level == "HIGH":
                confidence_score = 80.0
            else:
                confidence_score = 50.0
            findings.append({
                "id": str(uuid.uuid4()),
                "case_id": case_id,
                "title": f"{fraud_level} fraud risk detected",
                "description": f"Fraud intelligence engine classified case as {fraud_level}",
                "finding_type": "FRAUD_RISK",
                "severity": fraud_level,
                "confidence": confidence_score,  # Confidence score (0-100)
                "high_confidence_alerts": high_confidence_alerts,  # Jumlah alert
                "risk_score": 90 if fraud_level == "CRITICAL" else 70,
                "anomaly_score": 90,
                "detection_method": "FraudIntelligence",
                "engine": cls._get_engine_name("FraudIntelligence"),
                "anomaly_details": signals,
                "high_confidence_alerts": high_confidence_alerts,
                "metadata": {
                    "cluster_count": len(signals.get("high_risk_clusters", [])),
                    "hub_count": len(signals.get("hub_entities", [])),
                    "shared_pattern_count": len(signals.get("shared_package_patterns", [])),
                    "method_similarity_count": len(signals.get("method_similarity_patterns", []))
                },
                "recommendations": [
                    "Immediate investigation required",
                    "Review all connected vendors",
                    "Analyze shared package patterns",
                    "Prepare enforcement action"
                ]
            })

        # ==============================
        # GRAPH NETWORK
        # ==============================

        clusters = signals.get("high_risk_clusters", [])
        high_risk_clusters = [c for c in clusters if c.get("risk_level") == "HIGH"]

        if high_risk_clusters:
            recommendations = [
                "Review suspicious entity network",
                "Investigate connected vendors",
                "Expand graph traversal for hidden relationships",
                "Analyze hub entities for collusion patterns"
            ]
    
            if high_risk_count >= 3:
                recommendations.append(f"Prioritize investigation of {high_risk_count} high-risk clusters")
    
            if len(signals.get("hub_entities", [])) >= 5:
                recommendations.append("Focus on vendors with high centrality scores")
    
            if len(signals.get("shared_package_patterns", [])) >= 10:
                recommendations.append("Review shared package patterns between vendors")

        # Fraud finding
        if fraud_level in ["CRITICAL", "HIGH"]:
            recommendations = [
                "Immediate investigation required",
                "Review all connected vendors",
                "Analyze shared package patterns",
                "Prepare enforcement action"
            ]
    
            if len(signals.get("high_risk_clusters", [])) >= 4:
                recommendations.append("Prioritize cluster analysis for top 4 risk groups")
    
            if len(signals.get("hub_entities", [])) >= 5:
                recommendations.append("Investigate hub entities with highest degree centrality")

            total_clusters = len(clusters)
            high_risk_count = len(high_risk_clusters)

            # Narasi jelas
            if high_risk_count == total_clusters:
                description = f"{high_risk_count} high risk clusters detected in entity graph"
            else:
                description = f"{high_risk_count} high-risk clusters detected from {total_clusters} total clusters"

            recommendations = [
                "Review suspicious entity network",
                "Investigate connected vendors",
                "Expand graph traversal for hidden relationships",
                "Analyze hub entities for collusion patterns"
            ]

            # Rekomendasi berdasarkan cluster count
            if high_risk_count >= 3:
                recommendations.append("Prioritize investigation of top 3 high-risk clusters")

            # Rekomendasi berdasarkan hub entities
            if len(signals.get("hub_entities", [])) >= 5:
                recommendations.append("Focus on vendors with high centrality scores")

            findings.append({
                "id": str(uuid.uuid4()),
                "case_id": case_id,
                "title": "Suspicious graph network detected",
                "description": description,
                "finding_type": "GRAPH_ANOMALY",
                "severity": "HIGH",
                "confidence": 85.0,
                "risk_score": 80.0,
                "anomaly_score": 85.0,
                "detection_method": "GraphIntelligence",
                "engine": cls._get_engine_name("GraphIntelligence"),
                "anomaly_details": {
                    "total_clusters": total_clusters,
                    "high_risk_clusters": high_risk_count,
                    "clusters": clusters
                },
                "evidence_confidence": 75.0,
                "recommendations": recommendations
            })

        # ==============================
        # EVIDENCE QUALITY
        # ==============================

        evidence_score = float(evidence_data.get("score", 0))

        if evidence_score < 70:
            recommendations = [
                "Perform additional evidence validation",
                "Collect supporting documentation",
                "Review chain of custody",
                "Await analyst decision"
            ]

            # Rekomendasi berdasarkan verifikasi
            verified = evidence_data.get("verified", 0)
            total = evidence_data.get("total", 0)
            if total > 0 and verified < total * 0.5:
                recommendations.append("Prioritize verification of pending evidence")

            findings.append({
                "id": str(uuid.uuid4()),
                "case_id": case_id,
                "title": "Evidence quality requires review",
                "description": f"Evidence intelligence score is {evidence_score}",
                "finding_type": "EVIDENCE_QUALITY",
                "severity": "MEDIUM",
                "confidence": evidence_score,
                "risk_score": 60.0,
                "anomaly_score": 50.0,
                "detection_method": "EvidenceIntelligence",
                "engine": cls._get_engine_name("EvidenceIntelligence"),
                "anomaly_details": evidence_data,
                "recommendations": recommendations
            })

        return findings