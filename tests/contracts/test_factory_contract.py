from uuid import UUID

from backend.core.context import ExecutionContext
from backend.domain.enums import EngineStatus


class TestFactoryContract:
    """Factory Contract — Level 6."""

    def test_factory_creates_aggregate(
        self,
        app_container,
        collector_registry,
    ):
        factory = app_container.domain_services.factory

        case_id = UUID("446e216d-eb0e-487e-8e6b-ec943468ea20")
        context = ExecutionContext.create(case_id)

        result = factory.create_from_results(
            case_id=case_id,
            results=collector_registry,
            context=context,
        )

        assert result is not None
        assert result.case_id == str(case_id)

        assert result.fraud.total_patterns == 2
        assert result.fraud.engine_status == EngineStatus.OK

        assert result.graph.entities == 549
        assert result.graph.relationships == 5471

        assert result.risk.score == 82.0

        assert result.evidence.total == 9
        assert result.procurement.packages == 4

        assert result.confidence >= 0
        assert result.status is not None