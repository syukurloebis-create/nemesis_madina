"""
NEMESIS Madina - Graph Events Tests
"""

import pytest
from uuid import uuid4

from backend.domain.events.graph_events import GraphPayload, GraphAnalysisCompleted
from backend.domain.events.metadata import EventMetadata


class TestGraphEvents:
    def test_graph_payload_to_dict(self):
        payload = GraphPayload(
            case_id=uuid4(),
            entities=549,
            relationships=5471,
        )
        
        data = payload.to_dict()
        assert data["entities"] == 549
        assert data["relationships"] == 5471