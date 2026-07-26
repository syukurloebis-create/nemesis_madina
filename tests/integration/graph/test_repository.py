"""
Integration Tests - PostgresGraphRepository
"""

import pytest
import pytest_asyncio
from uuid import uuid4

from backend.graph.domain.node import GraphNode
from backend.graph.domain.edge import GraphEdge
from backend.graph.domain.aggregate import GraphAggregate
from backend.graph.domain.factory import GraphAggregateFactory
from backend.graph.infrastructure.repositories.postgres import PostgresGraphRepository
from backend.graph.infrastructure.repositories.metadata import GraphMetadataRepository
from backend.graph.infrastructure.mappers.to_orm import GraphToOrmMapper
from backend.graph.infrastructure.mappers.to_domain import OrmToGraphMapper
from backend.graph.infrastructure.factories.metadata import MetadataFactory
from backend.graph.infrastructure.services.checksum import CanonicalChecksumService
from backend.graph.infrastructure.interfaces.identity import UUIDIdentityGenerator


@pytest.mark.asyncio
class TestPostgresGraphRepository:
    """Integration tests for PostgresGraphRepository."""
    
    @pytest_asyncio.fixture
    async def repository(self, uow):
        """Create repository instance."""
        identity_generator = UUIDIdentityGenerator()
        to_orm_mapper = GraphToOrmMapper(identity_generator=identity_generator)
        factory = GraphAggregateFactory()
        to_domain_mapper = OrmToGraphMapper(factory=factory)
        metadata_repo = GraphMetadataRepository()
        checksum_service = CanonicalChecksumService()
        metadata_factory = MetadataFactory()
        
        return PostgresGraphRepository(
            to_orm_mapper=to_orm_mapper,
            to_domain_mapper=to_domain_mapper,
            metadata_repo=metadata_repo,
            checksum_service=checksum_service,
            metadata_factory=metadata_factory,
        )
    
    async def test_save_and_load_aggregate(self, repository, uow):
        """Save aggregate and load it back."""
        case_id = uuid4()
        institution_id = uuid4()
        
        node1 = GraphNode("vendor_001", "vendor", "PT A")
        node2 = GraphNode("vendor_002", "vendor", "PT B")
        edge = GraphEdge("vendor_001", "vendor_002", "COLLUSION", 0.8)
        
        aggregate = GraphAggregate(
            case_id=case_id,
            institution_id=institution_id,
            nodes=(node1, node2),
            edges=(edge,),
        )
        
        # Save
        version = await repository.save_aggregate(uow, aggregate)
        assert version == 1
        
        await uow.commit()
        
        # Load
        loaded = await repository.get_by_case(uow, case_id)
        
        assert loaded is not None
        assert loaded.case_id == case_id
        assert loaded.node_count == 2
        assert loaded.edge_count == 1
        assert loaded.version == 1
        
        # Verify nodes
        assert loaded.contains_node("vendor_001")
        assert loaded.contains_node("vendor_002")
        
        # Verify edges
        assert loaded.contains_edge("vendor_001", "vendor_002", "COLLUSION")
    
    async def test_save_with_merge_strategy(self, repository, uow):
        """Test merge strategy updates existing entities."""
        case_id = uuid4()
        institution_id = uuid4()
        
        # Initial save
        node1 = GraphNode("vendor_001", "vendor", "PT A")
        node2 = GraphNode("vendor_002", "vendor", "PT B")
        edge = GraphEdge("vendor_001", "vendor_002", "COLLUSION", 0.8)
        
        aggregate1 = GraphAggregate(
            case_id=case_id,
            institution_id=institution_id,
            nodes=(node1, node2),
            edges=(edge,),
        )
        
        await repository.save_aggregate(uow, aggregate1)
        await uow.commit()
        
        # Update with merge
        node1_updated = GraphNode("vendor_001", "vendor", "PT A Updated")
        node3 = GraphNode("vendor_003", "vendor", "PT C")
        edge2 = GraphEdge("vendor_001", "vendor_003", "CONTRACT", 0.5)
        
        aggregate2 = GraphAggregate(
            case_id=case_id,
            institution_id=institution_id,
            nodes=(node1_updated, node2, node3),
            edges=(edge, edge2),
        )
        
        from backend.graph.infrastructure.repositories.postgres import SaveStrategy
        await repository.save_aggregate(
            uow, aggregate2, strategy=SaveStrategy.MERGE
        )
        await uow.commit()
        
        # Load and verify
        loaded = await repository.get_by_case(uow, case_id)
        
        assert loaded is not None
        assert loaded.node_count == 3
        assert loaded.edge_count == 2
        
        # Check updated name
        node = loaded.get_node_by_key("vendor_001")
        assert node is not None
        assert node.name == "PT A Updated"
    
    async def test_delete_case_graph(self, repository, uow):
        """Test deleting graph data."""
        case_id = uuid4()
        institution_id = uuid4()
        
        node1 = GraphNode("vendor_001", "vendor", "PT A")
        node2 = GraphNode("vendor_002", "vendor", "PT B")
        edge = GraphEdge("vendor_001", "vendor_002", "COLLUSION", 0.8)
        
        aggregate = GraphAggregate(
            case_id=case_id,
            institution_id=institution_id,
            nodes=(node1, node2),
            edges=(edge,),
        )
        
        # Save
        await repository.save_aggregate(uow, aggregate)
        await uow.commit()
        
        # Delete
        await repository.delete_case_graph(uow, case_id)
        await uow.commit()
        
        # Verify deleted
        exists = await repository.exists(uow, case_id)
        assert exists is False
        
        loaded = await repository.get_by_case(uow, case_id)
        assert loaded is None