"""
Repository Factory - Centralized repository creation.
"""

from backend.repositories.sqlalchemy.risk_command_repository_impl import RiskCommandRepositoryImpl
from backend.repositories.sqlalchemy.risk_repository_impl import RiskRepositoryImpl  # ← ADD THIS
from backend.repositories.sqlalchemy.graph_repository_impl import GraphRepositoryImpl
from backend.repositories.sqlalchemy.evidence_repository_impl import EvidenceRepositoryImpl
from backend.repositories.sqlalchemy.fraud_repository_impl import FraudRepositoryImpl
from backend.repositories.sqlalchemy.procurement_repository_impl import ProcurementRepositoryImpl


class RepositoryFactory:
    """Factory for creating repository instances."""

    def __init__(self, sql_repo):
        self._sql_repo = sql_repo

    def fraud(self):
        return FraudRepositoryImpl(self._sql_repo)

    def graph(self):
        return GraphRepositoryImpl(self._sql_repo)

    def risk(self):
        """READ repository for Risk - used by Dashboard Intelligence."""
        return RiskRepositoryImpl(self._sql_repo)  # ← CHANGED!

    def risk_command(self):
        """WRITE repository for Risk - used by command handlers."""
        return RiskCommandRepositoryImpl()

    def evidence(self):
        return EvidenceRepositoryImpl(self._sql_repo)

    def procurement(self):
        return ProcurementRepositoryImpl(self._sql_repo)