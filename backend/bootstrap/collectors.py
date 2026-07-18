"""
Collectors Assembler — Create immutable collector registry.
"""

from backend.infrastructure.repository_factory import RepositoryFactory
from backend.infrastructure.unit_of_work import UnitOfWorkFactory  # ← TAMBAHKAN
from backend.collectors.registry import CollectorRegistry
from backend.collectors.fraud_collector import FraudCollector
from backend.collectors.graph_collector import GraphCollector
from backend.collectors.risk_collector import RiskCollector
from backend.collectors.evidence_collector import EvidenceCollector
from backend.collectors.procurement_collector import ProcurementCollector


def create_collector_registry(
    repo_factory: RepositoryFactory,
    uow_factory: UnitOfWorkFactory,  # ← TAMBAHKAN PARAMETER
) -> CollectorRegistry:
    """
    Create immutable collector registry.
    
    ✅ Collector menerima repository + uow_factory
    """
    collectors = {
        "fraud": FraudCollector(repo_factory.fraud(), uow_factory),
        "graph": GraphCollector(repo_factory.graph(), uow_factory),
        "risk": RiskCollector(repo_factory.risk(), uow_factory),
        "evidence": EvidenceCollector(repo_factory.evidence(), uow_factory),
        "procurement": ProcurementCollector(repo_factory.procurement(), uow_factory),
    }
    
    return CollectorRegistry(collectors)