# backend/scripts/test_regeneration.py
"""
Manual test of GraphRegenerationService before router creation.
"""

import asyncio
from uuid import UUID
from backend.bootstrap.container_builder import build_application_container
from backend.graph.application.dto import GraphBuildRequest

async def test_regeneration():
    """Test regeneration service directly."""
    # 1. Build container
    container = await build_application_container()
    
    # 2. Get service
    service = container.graph_regeneration
    uow_factory = container.uow_factory
    
    # 3. Build request (MOCK for now)
    request = GraphBuildRequest(
        case_id=UUID("55918f08-9ffa-41f0-8264-d0cda4ac5871"),
        institution_id=UUID("..."),  # Get from database
        # ... other fields
    )
    
    # 4. Execute
    async with uow_factory.create() as uow:
        aggregate, stats = await service.regenerate_graph(
            uow=uow,
            request=request,
            strategy="replace"
        )
        await uow.commit()
    
    print(f"✅ Regenerated: {len(aggregate.nodes)} entities, {len(aggregate.edges)} relationships")
    return aggregate

if __name__ == "__main__":
    asyncio.run(test_regeneration())