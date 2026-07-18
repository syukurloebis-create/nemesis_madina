from sqlalchemy import text
from backend.services.dashboard_cache_manager import (
    dashboard_cache_manager
)

class DashboardKPIService:


    CACHE_TTL = 60


    async def get_kpi(
        self,
        db
    ):

        cache = dashboard_cache_manager.get(
            "dashboard_kpi",
            "global"
        )


        if cache:

            return cache



        from backend.services.finding_intelligence_service import (
            finding_intelligence_service
        )


        result = await db.execute(
            text("""
                SELECT id
                FROM findings
            """)
        )


        findings = result.fetchall()


        total = len(findings)


        critical = 0
        high = 0
        medium = 0
        low = 0


        score_total = 0
        confidence_total = 0


        for row in findings:


            intelligence = await finding_intelligence_service.get_intelligence(
                str(row.id),
                db
            )


            risk = intelligence.get(
                "risk",
                intelligence
            )


            level = risk.get(
                "level",
                "UNKNOWN"
            )


            score = float(
                risk.get(
                    "intelligence_score",
                    0
                )
                or 0
            )

            score_total += score


            evidence = intelligence.get(
                "evidence",
                {}
            )


            confidence_total += float(
                evidence.get(
                    "confidence",
                    risk.get(
                        "drivers",
                        {}
                    ).get(
                        "evidence_confidence",
                        0
                    )
                )

            )


            if level == "CRITICAL":
                critical += 1

            elif level == "HIGH":
                high += 1

            elif level == "MEDIUM":
                medium += 1

            elif level == "LOW":
                low += 1



        response = {

            "kpi": {

                "total_findings":
                    total,


                "risk": {

                    "critical":
                        critical,

                    "high":
                        high,

                    "medium":
                        medium,

                    "low":
                        low,


                    "average_score":
                        round(
                            score_total / total,
                            2
                        )

                        if total
                        else 0,

                    "average_confidence":
                        round(
                            confidence_total / total,
                            2
                        )
                        if total
                        else 0

                }

            }

        }


        dashboard_cache_manager.set(
            "dashboard_kpi",
            "global",
            response
        )


        return response



dashboard_kpi_service = DashboardKPIService()