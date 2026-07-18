from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.entity_evidence_service import (
    entity_evidence_service
)


class EntityGraphIntelligenceService:

    # ============================================================
    # 1. METHOD BARU: calculate_fraud_score
    # ============================================================
    def calculate_fraud_score(
        self,
        summary: dict
    ) -> float:
        """
        Calculate fraud score based on graph intelligence signals
        Range: 0 - 100
        """
        score = 0

        # Identity risk
        score += min(
            summary.get("same_entity_candidate", 0) * 15,
            25
        )

        # Procurement collusion
        score += min(
            summary.get("shared_package", 0) * 8,
            35
        )

        # Procurement behavior similarity
        score += min(
            summary.get("method_similarity", 0) * 5,
            20
        )

        # Financial similarity
        score += min(
            summary.get("financial_similarity", 0) * 3,
            20
        )

        return min(round(score, 2), 100)

    # ============================================================
    # 2. METHOD BARU: calculate_confidence
    # ============================================================
    def calculate_confidence(
        self,
        summary: dict
    ) -> float:

        confidence = 0

        confidence += (
            summary.get(
                "same_entity_candidate",
                0
            )
            * 0.25
        )

        confidence += (
            summary.get(
                "shared_package",
                0
            )
            * 0.08
        )

        confidence += (
            summary.get(
                "method_similarity",
                0
            )
            * 0.05
        )

        confidence += (
            summary.get(
                "financial_similarity",
                0
            )
            * 0.05
        )

        confidence += (
            summary.get(
                "vendor_name_similarity",
                0
            )
            * 0.03
        )

        return round(
            min(confidence, 0.95),
            2
        )


    def calculate_evidence_grade(
        self,
        summary: dict,
        confidence: float,
        evidence
    ) -> str:
        """
        Evidence strength classification.

        Factors:
        - graph relationship signals
        - confidence score
        - evidence availability

        Output:
        STRONG
        MODERATE
        WEAK
        INSUFFICIENT
        """

        signal_count = sum(
            summary.values()
        )

        evidence_count = 0

        if isinstance(evidence, dict):
            evidence_count = len(evidence)

        elif isinstance(evidence, list):
            evidence_count = len(evidence)

        total_strength = (
            signal_count +
            evidence_count
        )

        #
        # Strong intelligence evidence
        #
        if (
            confidence >= 0.75
            and
            total_strength >= 10
        ):
            return "STRONG"

        #
        # Moderate evidence
        #
        elif (
            confidence >= 0.45
            and
            total_strength >= 5
        ):
            return "MODERATE"

        #
        # Weak evidence
        #
        elif total_strength >= 2:
            return "WEAK"

        return "INSUFFICIENT"

    # ============================================================
    # 3. METHOD BARU: generate_risk_explanation
    # ============================================================
    def generate_risk_explanation(
        self,
        summary: dict
    ) -> list:
        """
        Generate human-readable risk explanations
        """
        explanations = []

        if summary.get("same_entity_candidate", 0):
            explanations.append(
                f"{summary['same_entity_candidate']} duplicate identity signal detected"
            )

        if summary.get("shared_package", 0):
            explanations.append(
                f"{summary['shared_package']} procurement package relationship detected"
            )

        if summary.get("method_similarity", 0):
            explanations.append(
                f"{summary['method_similarity']} procurement behavior similarity detected"
            )

        if summary.get("financial_similarity", 0):
            explanations.append(
                f"{summary['financial_similarity']} financial similarity detected"
            )

        return explanations


    def calibrate_fraud_score(
        self,
        fraud_score: float,
        summary: dict,
        confidence: float
    ) -> float:
        """
        Calibration layer to reduce false positives.

        Adjust fraud score based on:
        - evidence strength
        - signal combination
        - confidence
        """

        calibrated = fraud_score


        #
        # 1. Weak signal penalty
        #
        total_signal = sum(
            summary.values()
        )

        if total_signal <= 2:
            calibrated -= 20


        #
        # 2. Name similarity alone penalty
        #
        if (
            summary.get(
                "vendor_name_similarity",
                0
            ) > 0
            and
            summary.get(
                "shared_package",
                0
            ) == 0
            and
            summary.get(
                "financial_similarity",
                0
            ) == 0
        ):
            calibrated -= 25


        #
        # 3. Confidence adjustment
        #
        if confidence < 0.3:
            calibrated -= 15


        elif confidence < 0.5:
            calibrated -= 5


        #
        # 4. Signal dominance control
        #

        identity = summary.get(
            "same_entity_candidate",
            0
        )

        collusion = summary.get(
            "shared_package",
            0
        )

        behavior = summary.get(
            "method_similarity",
            0
        )

        financial = summary.get(
            "financial_similarity",
            0
        )

        strong_signals = 0

        if identity >= 1:
            strong_signals += 1

        if collusion >= 5:
            strong_signals += 1

        if behavior >= 5:
            strong_signals += 1

        if financial >= 5:
            strong_signals += 1

        #
        # Penalize single-domain anomaly
        #

        if strong_signals == 1:
            calibrated -= 15

        #
        # Reward multi-domain fraud evidence
        #

        elif strong_signals >= 3:
            calibrated += 5


        #
        # 4. Strong fraud combination bonus
        #
        if (
            summary.get(
                "same_entity_candidate",
                0
            ) >= 1
            and
            summary.get(
                "shared_package",
                0
            ) >= 3
        ):
            calibrated += 10

        #
        # 5. Multi signal reinforcement
        #
        active_signals = sum(
            1
            for value in summary.values()
            if value > 0
        )

        if active_signals >= 3:
            calibrated += 5


        #
        # Normalize
        #
        return round(
            max(
                min(
                    calibrated,
                    100
                ),
                0
            ),
            2
        )

    # ============================================================
    # METHOD EXISTING: analyze_entity
    # ============================================================
    async def analyze_entity(
        self,
        entity_name,
        db
    ):
        network = await self.get_entity_network(
            entity_name,
            db
        )

        intelligence = network.get(
            "intelligence",
            {}
        )

        return {
            "name": entity_name,
            "fraud_score":
                intelligence.get(
                    "fraud_score",
                    0
                ),
            "risk_level":
                intelligence.get(
                    "risk_level",
                    "LOW"
                ),
            "confidence":
                intelligence.get(
                    "confidence",
                    0
                )
        }

    # ============================================================
    # METHOD EXISTING: get_entity_network (DIPERBAIKI)
    # ============================================================
    async def get_entity_network(
        self,
        entity_name: str,
        db: AsyncSession
    ):

        normalized = entity_name.upper()

        #
        # 1. FIND ENTITY
        #
        entity_result = await db.execute(
            text(
                """
                SELECT
                    id,
                    name,
                    entity_type,
                    risk_score
                FROM graph_entities
                WHERE UPPER(name)=:name
                LIMIT 1
                """
            ),
            {"name": normalized}
        )

        entity = entity_result.mappings().first()

        if not entity:
            return {
                "entity": None,
                "nodes": [],
                "relations": [],
                "patterns": [],
                "risk_explanation": [],
                "intelligence": {}
            }

        entity_id = entity["id"]

        #
        # 2. GRAPH RELATIONS
        #
        relation_result = await db.execute(
            text(
                """
                SELECT
                    gr.relationship_type,
                    gr.weight,
                    source.id AS source_id,
                    source.name AS source_name,
                    target.id AS target_id,
                    target.name AS target_name
                FROM graph_relationships gr
                JOIN graph_entities source ON source.id = gr.source_id
                JOIN graph_entities target ON target.id = gr.target_id
                WHERE
                    (gr.source_id = :entity_id OR gr.target_id = :entity_id)
                    AND gr.relationship_type IN (
                        'same_entity_candidate',
                        'vendor_name_similarity',
                        'shared_package',
                        'method_similarity',
                        'financial_similarity'
                    )
                ORDER BY gr.weight DESC
                LIMIT 100
                """
            ),
            {"entity_id": entity_id}
        )

        rows = relation_result.mappings().all()

        #
        # 3. BUILD NODES & RELATIONS
        #
        nodes = {}
        relations = []
        summary = {
            "same_entity_candidate": 0,
            "vendor_name_similarity": 0,
            "shared_package": 0,
            "method_similarity": 0,
            "financial_similarity": 0
        }

        for row in rows:
            relation_type = row["relationship_type"]
            weight = float(row["weight"])

            summary[relation_type] += 1

            source_id = str(row["source_id"])
            target_id = str(row["target_id"])

            # Nodes
            if source_id not in nodes:
                nodes[source_id] = {
                    "id": source_id,
                    "name": row["source_name"],
                    "type": "vendor",
                    "risk_score": 0
                }

            if target_id not in nodes:
                nodes[target_id] = {
                    "id": target_id,
                    "name": row["target_name"],
                    "type": "vendor",
                    "risk_score": 0
                }

            # Relations
            relations.append({
                "source": row["source_name"],
                "target": row["target_name"],
                "type": relation_type,
                "weight": weight
            })

        #
        # 4. CALCULATE NODE RISK SCORES
        #
        for node in nodes.values():
            related = [
                r for r in relations
                if r["source"] == node["name"] or r["target"] == node["name"]
            ]

            shared_package_count = sum(1 for r in related if r["type"] == "shared_package")
            method_similarity_count = sum(1 for r in related if r["type"] == "method_similarity")
            financial_similarity_count = sum(1 for r in related if r["type"] == "financial_similarity")

            node["risk_score"] = min(
                (shared_package_count * 8) +
                (method_similarity_count * 5) +
                (financial_similarity_count * 3),
                100
            )

        #
        # 5. EXTRACT SIGNALS
        #
        same_entity = summary["same_entity_candidate"]
        name_similarity = summary["vendor_name_similarity"]
        shared_package = summary["shared_package"]
        method_similarity = summary["method_similarity"]
        financial_similarity = summary["financial_similarity"]

        #
        # 6. PATTERN DETECTION (SAMA, TIDAK DIUBAH)
        #
        patterns = []
        risk_explanation = []

        # Duplicate Identity
        if same_entity >= 2:
            patterns.append({
                "type": "DUPLICATE_VENDOR_IDENTITY",
                "severity": "HIGH",
                "evidence": same_entity,
                "description": f"{same_entity} vendor identity duplication candidate(s)"
            })
            risk_explanation.append(
                f"Vendor has {same_entity} duplicate identity candidate(s)"
            )
        elif same_entity == 1:
            patterns.append({
                "type": "DUPLICATE_VENDOR_IDENTITY",
                "severity": "MEDIUM",
                "evidence": same_entity,
                "description": f"{same_entity} vendor identity duplication candidate(s)"
            })
            risk_explanation.append(
                f"Vendor has {same_entity} duplicate identity candidate(s)"
            )

        # Package Collusion
        if shared_package >= 5:
            patterns.append({
                "type": "PACKAGE_COLLUSION",
                "severity": "HIGH",
                "evidence": shared_package,
                "description": f"{shared_package} vendors share procurement packages"
            })
            risk_explanation.append(
                f"Vendor shares packages with {shared_package} vendor(s)"
            )
        elif shared_package >= 2:
            patterns.append({
                "type": "PACKAGE_COLLUSION",
                "severity": "MEDIUM",
                "evidence": shared_package,
                "description": f"{shared_package} vendors share procurement packages"
            })
            risk_explanation.append(
                f"Vendor shares packages with {shared_package} vendor(s)"
            )

        # Procurement Method Pattern
        if method_similarity >= 10:
            patterns.append({
                "type": "PROCUREMENT_METHOD_PATTERN",
                "severity": "HIGH",
                "evidence": method_similarity,
                "description": f"{method_similarity} vendors show strong procurement behavior similarity"
            })
            risk_explanation.append(
                f"Vendor shows procurement behavior similarity with {method_similarity} vendor(s)"
            )
        elif method_similarity >= 5:
            patterns.append({
                "type": "PROCUREMENT_METHOD_PATTERN",
                "severity": "MEDIUM",
                "evidence": method_similarity,
                "description": f"{method_similarity} vendors show procurement behavior similarity"
            })
            risk_explanation.append(
                f"Vendor shows procurement behavior similarity with {method_similarity} vendor(s)"
            )
        elif method_similarity >= 2:
            patterns.append({
                "type": "PROCUREMENT_METHOD_PATTERN",
                "severity": "LOW",
                "evidence": method_similarity,
                "description": f"{method_similarity} vendors show procurement behavior similarity"
            })
            risk_explanation.append(
                f"Vendor shows procurement behavior similarity with {method_similarity} vendor(s)"
            )

        # Financial Cluster
        if financial_similarity >= 10:
            patterns.append({
                "type": "FINANCIAL_CLUSTER",
                "severity": "HIGH",
                "evidence": financial_similarity,
                "description": f"{financial_similarity} vendors show strong financial similarity"
            })
            risk_explanation.append(
                f"Vendor shows financial similarity with {financial_similarity} vendor(s)"
            )
        elif financial_similarity >= 5:
            patterns.append({
                "type": "FINANCIAL_CLUSTER",
                "severity": "MEDIUM",
                "evidence": financial_similarity,
                "description": f"{financial_similarity} vendors show financial similarity"
            })
            risk_explanation.append(
                f"Vendor shows financial similarity with {financial_similarity} vendor(s)"
            )
        elif financial_similarity >= 2:
            patterns.append({
                "type": "FINANCIAL_CLUSTER",
                "severity": "LOW",
                "evidence": financial_similarity,
                "description": f"{financial_similarity} vendors show financial similarity"
            })
            risk_explanation.append(
                f"Vendor shows financial similarity with {financial_similarity} vendor(s)"
            )

        # Identity Laundering (Combo)
        if same_entity > 0 and financial_similarity >= 3:
            patterns.append({
                "type": "IDENTITY_LAUNDERING",
                "severity": "CRITICAL",
                "evidence": same_entity + financial_similarity,
                "description": "Duplicate vendor identity combined with financial similarity"
            })

        # Combo: Procurement Collusion Network
        if shared_package >= 5 and method_similarity >= 3:
            patterns.append({
                "type": "PROCUREMENT_COLLUSION_NETWORK",
                "severity": "HIGH",
                "evidence": shared_package + method_similarity,
                "description": f"Strong collusion network: {shared_package} shared packages, {method_similarity} similar methods"
            })

        # Combo: Financial + Behavior Cluster
        if financial_similarity >= 5 and method_similarity >= 5:
            patterns.append({
                "type": "FINANCIAL_BEHAVIOR_CLUSTER",
                "severity": "HIGH",
                "evidence": financial_similarity + method_similarity,
                "description": f"Strong financial ({financial_similarity}) and behavior ({method_similarity}) cluster"
            })

        # ============================================================
        # 7. SCORING ENGINE - REPLACED
        # ============================================================

        # ✅ BARU: Gunakan method calculate_fraud_score
        raw_score = self.calculate_fraud_score(summary)

        confidence = self.calculate_confidence(summary)

        fraud_score = self.calibrate_fraud_score(
            raw_score,
            summary,
            confidence
        )

        # ✅ BARU: Gunakan method generate_risk_explanation
        generated_explanation = self.generate_risk_explanation(summary)

        # Gabungkan dengan risk_explanation existing
        risk_explanation = generated_explanation + risk_explanation

        #
        # 8. INTELLIGENCE CLASSIFICATION (TIDAK DIUBAH)
        #
        identity_score = min(summary.get("same_entity_candidate", 0) * 15, 25)
        collusion_score = min(summary.get("shared_package", 0) * 8, 35)
        financial_score = min(summary.get("financial_similarity", 0) * 3, 20)

        signal_count = 0

        if identity_score >= 15:
            signal_count += 1

        if collusion_score >= 15:
            signal_count += 1

        if financial_score >= 15:
            signal_count += 1

        if signal_count >= 3:
            intelligence_type = "MULTI_SIGNAL_FRAUD"

        elif collusion_score >= 25:
            intelligence_type = "NETWORK_COLLUSION"

        elif identity_score >=15:
            intelligence_type = "IDENTITY_RISK"

        elif financial_score >=15:
            intelligence_type = "FINANCIAL_CLUSTER"

        else:
            intelligence_type = "BEHAVIORAL_ANOMALY"

        #
        # 9. EVIDENCE LAYER (TIDAK DIUBAH)
        #
        evidence = await entity_evidence_service.build_evidence(
            entity_id,
            entity["name"],
            db
        )

        evidence_grade = self.calculate_evidence_grade(
            summary,
            confidence,
            evidence
        )


        # ============================================================
        # RISK PATTERN GATE
        # ============================================================

        critical_patterns = [
            "IDENTITY_LAUNDERING",
            "PROCUREMENT_COLLUSION_NETWORK",
            "FINANCIAL_BEHAVIOR_CLUSTER"
        ]

        critical_found = any(
            p["type"] in critical_patterns
            for p in patterns
        )

        high_patterns = [
            "PACKAGE_COLLUSION",
            "PROCUREMENT_METHOD_PATTERN",
            "FINANCIAL_CLUSTER"
        ]

        high_pattern_found = any(
            p["type"] in high_patterns
            for p in patterns
        )

        strong_evidence = (
            confidence >= 0.75
            and
            evidence_grade in [
                "STRONG",
                "MODERATE"
            ]
        )

        # ============================================================
        # RISK CLASSIFICATION
        # ============================================================

        critical_evidence = (
            summary.get(
                "same_entity_candidate",
                0
            ) >= 1
            and
            (
                summary.get(
                    "financial_similarity",
                    0
                ) >= 5
                or
                summary.get(
                    "shared_package",
                    0
                ) >= 8
            )
        )

        if (
            fraud_score >= 85
            and
            critical_evidence
        ):
            risk_level = "CRITICAL"

        elif (
            fraud_score >=70
            and
            high_pattern_found
        ):
            risk_level = "HIGH"

        elif fraud_score >= 45:
            risk_level = "MEDIUM"

        else:
            risk_level = "LOW"


        print(
            "\nINTELLIGENCE CALIBRATION",
            entity["name"],
            {
                "raw": raw_score,
                "calibrated": fraud_score,
                "confidence": confidence,
                "evidence_grade": evidence_grade,
                "patterns": [
                    p["type"]
                    for p in patterns
                ],
                "summary": summary
            }
        )

        #
        # 11. RESPONSE (DIPERBAIKI: tambah confidence & risk_explanation)
        #
        return {
            "entity": {
                "id": entity["id"],
                "name": entity["name"],
                "type": entity["entity_type"],
                "fraud_score": fraud_score,
                "risk_score": fraud_score,
                "risk_level": risk_level,
                "confidence": confidence
            },
            "nodes": list(nodes.values()),
            "relations": relations,
            "patterns": patterns,
            "risk_explanation": risk_explanation,
            "intelligence": {
                "relationship_summary": summary,
                "fraud_score": fraud_score,
                "pattern_count": len(patterns),
                "risk_level": risk_level,
                "confidence": confidence,
                "intelligence_type": intelligence_type,
                "risk_explanation": risk_explanation,
                "evidence_grade": evidence_grade,
                "raw_score": raw_score,
                "calibrated_score": fraud_score,
                "score_explanation": {
                    "signals": {
                        "identity":
                            identity_score,
                        "collusion":
                            collusion_score,
                        "behavior":
                            min(
                                summary.get(
                                    "method_similarity",
                                    0
                                ) * 5,
                                20
                            ),
                        "financial":
                            financial_score
                    },
                    "base_score":
                        raw_score,
                    "calibration": {
                        "confidence_bonus":
                            round(
                                fraud_score - raw_score,
                                2
                            )
                            if fraud_score > raw_score
                            else 0,
                        "false_positive_penalty":
                            round(
                                raw_score - fraud_score,
                                2
                            )
                            if fraud_score < raw_score
                            else 0
                    },
                    "confidence":
                        confidence,
                    "final_score":
                        fraud_score
                },
                "relationship_metrics": {
                    "identity": same_entity,
                    "collusion": shared_package,
                    "behavior": method_similarity,
                    "financial": financial_similarity
                },
                "evidence": evidence
            }
        }


entity_graph_intelligence_service = EntityGraphIntelligenceService()