# services/finding_retrieval_service.py

import logging
from typing import Dict, Any

from sqlalchemy import text


logger = logging.getLogger(__name__)


class FindingRetrievalService:
    """
    Finding retrieval and aggregation layer
    """


    @staticmethod
    async def get_case_findings(
        case_id: str,
        db
    ) -> Dict[str, Any]:

        result = await db.execute(
            text(
                """
                SELECT
                    id,
                    title,
                    finding_type,
                    severity,
                    status,
                    confidence,
                    risk_score,
                    detection_method,
                    created_at,
                    updated_at

                FROM findings

                WHERE case_id=:case_id

                ORDER BY created_at DESC
                """
            ),
            {
                "case_id": case_id
            }
        )


        rows = result.fetchall()


        if not rows:
            return {
                "total":0,
                "summary":{},
                "latest":[]
            }


        findings=[]


        severity_summary={}

        status_summary={}


        for row in rows:

            severity = row.severity or "UNKNOWN"
            status = row.status or "UNKNOWN"


            severity_summary[severity] = (
                severity_summary.get(severity,0)+1
            )


            status_summary[status] = (
                status_summary.get(status,0)+1
            )


            findings.append(
                {
                    "id":row.id,
                    "title":row.title,
                    "type":row.finding_type,
                    "severity":severity,
                    "status":status,
                    "confidence":row.confidence,
                    "risk_score":row.risk_score,
                    "engine":row.detection_method,
                    "created_at":(
                        row.created_at.isoformat()
                        if row.created_at
                        else None
                    )
                }
            )


        return {

            "total":len(findings),

            "summary":{
                "severity":severity_summary,
                "status":status_summary
            },

            "latest":findings[:10]

        }