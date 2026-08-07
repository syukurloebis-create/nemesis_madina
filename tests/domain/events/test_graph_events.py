"""
NEMESIS Madina - Graph Events Tests
"""

import pytest
from uuid import uuid4

from backend.domain.events.graph_events import GraphPayload, GraphAnalysisCompleted
from backend.domain.events.metadata import EventMetadata
from backend.domain.value_objects.case_id import CaseId


class TestGraphEvents:
    def test_graph_payload_to_dict(self):
        payload = GraphPayload(
            case_id=CaseId(str(uuid4())),
            nodes=[],
            edges=[],
            cluster_count=0,
            max_cluster_size=0,
            density=0.0,
            diameter=0,
            avg_path_length=0.0,
            has_cycles=False,
            complexity_score=0.0,
            status="SUCCESS",
        )

        data = payload.to_dict()
        assert data["cluster_count"] == 0
        assert data["density"] == 0.0
        assert data["has_cycles"] is False