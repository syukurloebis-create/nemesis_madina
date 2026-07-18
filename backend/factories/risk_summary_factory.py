class RiskSummaryFactory:
    """Pure composition for Risk."""
    
    @staticmethod
    def create(
        collector: RiskCollectorDTO,
        calculation: CalculatedRisk
    ) -> RiskSummary:
        return RiskSummary(
            score=calculation.score,
            level=calculation.level,
            anomaly_score=calculation.anomaly_score,
            collusion_score=calculation.collusion_score,
            financial_score=calculation.financial_score,
            recommendations=list(calculation.recommendations),
            engine_status=calculation.engine_status,
        )