# backend/dashboard/policies/scoring_policy.py

from dataclasses import dataclass
from typing import List, Iterable
from backend.domain.summary_objects import (
    RiskSummary,
    FraudSummary,
    GraphSummary,
    EvidenceSummary,
    ProcurementSummary
)
from backend.domain.enums import EngineStatus
from backend.domain.summary_base import BaseSummary


class DashboardScoringPolicy:


    def determine_overall_status(
        self,
        summaries: Iterable[BaseSummary],
    ) -> str:
        """
        Determine overall dashboard status based on engine_status and has_data.
    
        Returns:
            "EMPTY" - Tidak ada data sama sekali
            "FAILED" - Ada engine yang gagal
            "PARTIAL" - Ada engine yang PARTIAL
            "OK" - Semua engine OK atau berhasil
        """
        summaries = tuple(summaries)

        if not summaries:
            return "EMPTY"

        if not any(s.has_data for s in summaries):
            return "EMPTY"

        if any(s.engine_status == EngineStatus.FAILED for s in summaries):
            return "FAILED"

        if any(s.engine_status == EngineStatus.PARTIAL for s in summaries):
            return "PARTIAL"

        return "OK"
    

    def has_any_data(self, summaries: Iterable[BaseSummary]) -> bool:
        """Check if any summary has actual data."""
        for summary in summaries:
            if summary.has_data:
                return True
            if hasattr(summary, 'score') and summary.score > 0:
                return True
        return False


    def calculate_total_risk(
        self,
        risk_score: float,
        fraud_score: float,
        evidence_score: float,
        graph_score: float,
        procurement_score: float,
    ) -> float:
        """Calculate total risk score from all components."""
        scores = [risk_score, fraud_score, evidence_score, graph_score, procurement_score]
        valid_scores = [s for s in scores if s > 0]
        if not valid_scores:
            return 0.0
        return sum(valid_scores) / len(valid_scores)