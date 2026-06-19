class DashboardMetrics:

    @staticmethod
    def summarize(results):

        total = len(results)

        high_risk = sum(
            1
            for r in results
            if r["risk_level"] == "HIGH"
        )

        medium_risk = sum(
            1
            for r in results
            if r["risk_level"] == "MEDIUM"
        )

        low_risk = sum(
            1
            for r in results
            if r["risk_level"] == "LOW"
        )

        avg_trust = (
            sum(
                r["trust_score"]
                for r in results
            )
            / total
            if total
            else 0
        )

        return {
            "total_entities": total,
            "high_risk": high_risk,
            "medium_risk": medium_risk,
            "low_risk": low_risk,
            "average_trust": round(avg_trust, 4)
        }