from pydantic import BaseModel


class DashboardSummary(
    BaseModel
):
    total_cases:int
    total_evidence:int
    verified:int
    rejected:int