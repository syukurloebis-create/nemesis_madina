# backend/dashboard/pipelines/risk_pipeline.py

from backend.dashboard.pipelines.base import Pipeline
from backend.dashboard.protocols.pipeline_context import PipelineContext
from backend.collectors.risk_collector import RiskCollector
from backend.calculators.risk_score_calculator import RiskScoreCalculator
from backend.mappers.risk_mapper import RiskMapper
from backend.domain.summary_objects import RiskSummary


class RiskPipeline(Pipeline[str, RiskSummary]):
    """Risk Pipeline: Collector → Calculator → Mapper."""
    
    def __init__(
        self,
        collector: RiskCollector,
        calculator: RiskScoreCalculator,
        mapper: RiskMapper
    ):
        self._collector = collector
        self._calculator = calculator
        self._mapper = mapper
    
    # NO name property - registry handles identification
    
    async def execute(self, context: PipelineContext) -> RiskSummary:
        dto = await self._collector.collect(context.case_id)
        calculated = self._calculator.calculate(dto)
        return self._mapper.to_summary(dto, calculated)