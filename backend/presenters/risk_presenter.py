class RiskPresenter:
    """Pure serializer for Risk."""
    
    @staticmethod
    def to_api_response(summary: RiskSummary) -> dict:
        return {
            "score": summary.score,
            "level": summary.level.value,
            "anomaly_score": summary.anomaly_score,
            "collusion_score": summary.collusion_score,
            "financial_score": summary.financial_score,
            "recommendations": summary.recommendations,
            "engine": summary.engine,
            "engine_status": summary.engine_status.value,
        }