"""
NEMESIS V8+

Finding Intelligence Service

Aggregates:
- Finding profile
- Timeline behavior
- Investigation progress
- Evidence confidence
- Decision intelligence
"""


from sqlalchemy import text
import logging
import time

from backend.services.dashboard_cache_manager import (
    dashboard_cache_manager
)


logger = logging.getLogger(__name__)


class FindingIntelligenceService:


    async def get_intelligence(
        self,
        finding_id: str,
        db
    ):


        cached = dashboard_cache_manager.get(
            "finding_intelligence",
            finding_id
        )


        if cached:

            logger.info(
                f"CACHE HIT finding_intelligence:{finding_id}"
            )

            return cached


        finding = await self.get_finding(
            finding_id,
            db
        )


        if not finding:

            return {
                "error":"Finding not found"
            }



        timeline = await self.get_timeline_context(
            finding_id,
            db
        )


        evidence = await self.get_evidence_context(
            finding_id,
            db
        )


        decision = await self.get_decision_context(
            finding_id,
            db
        )


        risk = self.calculate_risk_context(
            finding,
            timeline,
            evidence,
            decision
        )


        # =====================================
        # Normalize risk object
        # =====================================

        base_score = risk.get(
            "base_score",
            0
        )


        score = risk.get(
            "intelligence_score",
            0
        )


        level = risk.get(
            "level",
            "UNKNOWN"
        )


        drivers = risk.get(
            "drivers",
            {}
        )


        explanations = risk.get(
            "explanations",
            []
        )


        recommendations = (
            self.generate_recommendations(
                finding,
                timeline,
                evidence,
                risk,
                decision
            )
        )

        
        response = {

            "base_score": round(base_score,2),

            "intelligence_score": round(score,2),

            "delta": round(score-base_score,2),

            "level": level,

            "drivers": drivers,

            "explanations": explanations,

            "timeline": timeline,

            "evidence": evidence,

            "decision": decision,

            "recommendations": recommendations
        }


        dashboard_cache_manager.set(
            "finding_intelligence",
            finding_id,
            response
        )


        logger.info(
            f"CACHE SET finding_intelligence:{finding_id}"
        )


        return response
        

    async def get_finding(
        self,
        finding_id,
        db
    ):

        result = await db.execute(
            text("""
                SELECT
                    id,
                    title,
                    severity,
                    status,
                    confidence,
                    risk_score,
                    anomaly_score
                FROM findings
                WHERE id=:id
            """),
            {
                "id":finding_id
            }
        )


        row=result.fetchone()


        if not row:
            return None


        return dict(row._mapping)



    async def get_timeline_context(
        self,
        finding_id,
        db
    ):

        from backend.services.finding_timeline_service import (
            FindingTimelineService
        )


        service = FindingTimelineService(db)


        timeline = await service.get_timeline(
            finding_id
        )


        events = len(timeline)


        sla_breach = len(
            [
                x for x in timeline
                if x["event"]=="ASSIGNMENT_SLA_BREACHED"
            ]
        )


        evidence_actions = len(
            [
                x for x in timeline
                if x["event"]=="EVIDENCE_REVIEWED"
            ]
        )


        return {

            "events": events,

            "sla_breach": sla_breach,

            "evidence_actions": evidence_actions,

            "last_event":
                timeline[-1]
                if timeline
                else None
        }


    async def get_decision_context(
        self,
        finding_id,
        db
    ):

        result = await db.execute(
            text("""
                SELECT
                    decision,
                    confidence_score,
                    decided_by,
                    decided_at

                FROM finding_review_decisions

                WHERE finding_id=:id

                ORDER BY decided_at DESC

                LIMIT 1
            """),
            {
                "id":finding_id
            }
        )


        row=result.fetchone()


        if not row:

            return {

                "status":"PENDING",

                "confidence":0,

                "actor":None

            }


        return {

            "status":
                row.decision,

            "confidence":
                float(
                    row.confidence_score or 0
                ),

            "actor":
                row.decided_by,

            "timestamp":
                row.decided_at
        }


    async def get_evidence_context(
        self,
        finding_id,
        db
    ):

        # ======================================
        # PRIMARY SOURCE
        # evidence table
        # ======================================

        result = await db.execute(
            text("""
                SELECT
                    COUNT(*) AS total,
                    AVG(confidence_score) AS confidence

                FROM evidence

                WHERE id IN
                (
                    SELECT jsonb_array_elements_text(
                        evidence_ids::jsonb
                    )

                    FROM findings

                    WHERE id=:id
                )
            """),
            {
                "id": finding_id
            }
        )


        row = result.fetchone()


        total = row.total or 0

        confidence = float(
            row.confidence or 0
        )


        source = "evidence"



        # ======================================
        # FALLBACK
        # finding_action_logs
        # ======================================

        if total == 0:


            result = await db.execute(
                text("""
                    SELECT
                        COUNT(*) AS total

                    FROM finding_action_logs

                    WHERE finding_id=:id

                    AND action_type='EVIDENCE_REVIEWED'
                """),
                {
                    "id": finding_id
                }
            )



            action_row = result.fetchone()


            action_total = (
                action_row.total or 0
            )


            if action_total > 0:

                total = action_total


                # Evidence activity confidence model
                #
                # 1 review  = 40
                # 2 review  = 80
                # 3+ review = 90

                confidence = min(
                    action_total * 40,
                    90
                )


                source = (
                    "finding_action_logs"
                )



        return {

            "total":
                total,

            "confidence":
                confidence,

            "source":
                source

        }


    def calculate_risk_context(
        self,
        finding,
        timeline,
        evidence,
        decision
    ):


        score = float(
            finding.get(
                "risk_score",
                0
            )
            or 0
        )

        explanations = []



        # ==========================
        # Timeline pressure
        # ==========================

        if timeline.get("sla_breach", 0) > 0:
            score += 10
            if "explanations" not in locals():
                explanations = []
            explanations.append(
                "Assignment SLA breach detected"
            )


        if timeline.get("evidence_actions",0) > 0:

            explanations.append(
                f"{timeline.get('evidence_actions')} evidence review actions performed"
            )


        if timeline.get("evidence_actions",0) > 3:

            score += 5


        # ==========================
        # Evidence confidence
        # ==========================

        evidence_confidence = float(
            evidence.get(
                "confidence",
                0
            )
            or 0
        )


        if evidence_confidence < 50:
            score += 10
            explanations.append(
                "Low evidence confidence requires additional validation"
            )


        # ==========================
        # Decision Intelligence
        # ==========================

        decision_status = decision.get(
            "status",
        )

        decision_confidence = float(
            decision.get(
                "confidence",
                0
            )
            or 0
        )

        if decision_status == "CONFIRMED":

            explanations.append(
                "Analyst confirmed finding"
            )


        elif decision_status == "REJECTED":

            explanations.append(
                "Finding rejected by investigator"
            )


        if decision_confidence >= 0.9:

            score += 5

            explanations.append(
                "High confidence investigation decision"
            )


        decision_confidence = float(
            decision.get(
                "confidence",
                0
            )
            or 0
        )


        if decision_status == "CONFIRMED":
            score += 15


        elif decision_status == "REJECTED":
            score -= 20


        if decision_confidence >= 80:
            score += 5


        # ==========================
        # Normalize
        # ==========================

        score = min(
            score,
            100
        )


        if score >= 80:
            level = "CRITICAL"

        elif score >= 60:
            level = "HIGH"

        elif score >= 40:
            level = "MEDIUM"

        else:
            level = "LOW"


        return {

            "base_score":
                float(
                    finding.get(
                        "risk_score",
                        0
                    )
                    or 0
                ),


            "intelligence_score":
                round(
                    score,
                    2
                ),


            "level":
                level,


            "drivers": {

                "finding_risk":
                    finding.get(
                        "risk_score",
                        0
                    ),

                "sla_breach":
                    timeline.get(
                        "sla_breach",
                        0
                    ),

                "evidence_confidence":
                    evidence_confidence,

                "decision_status":
                    decision.get(
                        "status"
                    ),

                "decision_confidence":
                    decision.get(
                        "confidence",
                        0
                    )
            },


            "explanations":
                explanations
        }


    def generate_recommendations(
        self,
        finding,
        timeline,
        evidence,
        risk,
        decision
    ):

        actions = []


        risk_level = risk.get(
            "level",
            "LOW"
        )


        decision_status = decision.get(
            "status",
            "PENDING"
        )


        evidence_confidence = float(
            evidence.get(
                "confidence",
                0
            )
            or 0
        )


        # ==================================
        # Evidence validation
        # ==================================

        if evidence_confidence < 70:

            actions.append(
                "Perform additional evidence validation"
            )


        # ==================================
        # Investigation state
        # ==================================

        if decision_status == "PENDING":

            actions.append(
                "Await analyst decision"
            )


        # ==================================
        # SLA management
        # ==================================

        if timeline.get(
            "sla_breach",
            0
        ) > 0:

            actions.append(
                "Review SLA breach cause"
            )


        # ==================================
        # Confirmed high risk finding
        # ==================================

        if (
            decision_status == "CONFIRMED"
            and
            risk_level in [
                "HIGH",
                "CRITICAL"
            ]
        ):

            actions.append(
                "Escalate investigator review"
            )


            actions.append(
                "Prepare enforcement action"
            )


            actions.append(
                "Generate final investigation report"
            )


        # ==================================
        # Rejected finding
        # ==================================

        if decision_status == "REJECTED":

            actions.append(
                "Archive investigation evidence"
            )


        # ==================================
        # Default
        # ==================================

        if not actions:

            actions.append(
                "Continue monitoring"
            )


        return actions



finding_intelligence_service = (
    FindingIntelligenceService()
)