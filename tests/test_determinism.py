# tests/test_determinism.py (FIXED - Full file)
import sys
import pytest
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from metadata_inventory.contracts import (
    ArtifactId, ArtifactEnvelope, NodeDefinition,
    Dependency, DependencyType, ExecutionRecord
)
from metadata_inventory.artifact_factory import ArtifactFactory
from metadata_inventory.immutable_store import AppendOnlyArtifactStore
from metadata_inventory.typed_dag import TypedDAG
from metadata_inventory.execution_plan import ExecutionPlanner
from metadata_inventory.canonical_serializer import CanonicalSerializer, Fingerprint
from metadata_inventory.deterministic_jitter import DeterministicJitter


class TestDeterminism:
    """Property tests for determinism."""
    
    def test_artifact_id_deterministic(self):
        """Artifact ID must be deterministic based on content."""
        # Same content → same ID
        id1 = ArtifactId.from_content(
            name="test",
            payload={"key": "value"},
            producer="test",
            schema_version="1.0"
        )
        id2 = ArtifactId.from_content(
            name="test",
            payload={"key": "value"},
            producer="test",
            schema_version="1.0"
        )
        assert id1.value == id2.value
        
        # Different content → different ID
        id3 = ArtifactId.from_content(
            name="test",
            payload={"key": "different"},
            producer="test",
            schema_version="1.0"
        )
        assert id1.value != id3.value
    
    def test_artifact_fingerprint_deterministic(self):
        """Artifact fingerprint must be deterministic."""
        # TIDAK ADA IMPORT INTERNAL - langsung gunakan ArtifactEnvelope dari import atas
        env1 = ArtifactEnvelope.create(
            name="test",
            payload={"key": "value"},
            producer="test",
            schema_version="1.0"
        )
        env2 = ArtifactEnvelope.create(
            name="test",
            payload={"key": "value"},
            producer="test",
            schema_version="1.0"
        )
        
        # Same content → same fingerprint
        assert env1.checksum == env2.checksum
        
        # Different content → different fingerprint
        env3 = ArtifactEnvelope.create(
            name="test",
            payload={"key": "different"},
            producer="test",
            schema_version="1.0"
        )
        assert env1.checksum != env3.checksum
    
    def test_canonical_serializer_stable(self):
        """Canonical serializer must produce stable output."""
        obj1 = {"a": 1, "b": 2, "c": {"d": 3}}
        obj2 = {"a": 1, "b": 2, "c": {"d": 3}}
        
        ser1 = CanonicalSerializer.serialize(obj1)
        ser2 = CanonicalSerializer.serialize(obj2)
        assert ser1 == ser2
        
        obj3 = {"c": {"d": 3}, "a": 1, "b": 2}
        ser3 = CanonicalSerializer.serialize(obj3)
        assert ser1 == ser3
    
    def test_execution_plan_deterministic(self):
        """Execution plan must be deterministic."""
        def build_dag():
            dag = TypedDAG()
            
            async def runner1(inputs):
                return {"result": "value1"}
            
            async def runner2(inputs):
                return {"result": "value2"}
            
            dag.register_node(
                name="node1",
                engine="test",
                depends_on=[],
                input_types={},
                output_type=dict,
                runner=runner1
            )
            dag.register_node(
                name="node2",
                engine="test",
                depends_on=[Dependency("node1", DependencyType.HARD)],
                input_types={"node1": dict},
                output_type=dict,
                runner=runner2
            )
            return dag
        
        dag1 = build_dag()
        dag2 = build_dag()
        
        planner1 = ExecutionPlanner(dag1._nodes)
        planner2 = ExecutionPlanner(dag2._nodes)
        plan1 = planner1.plan()
        plan2 = planner2.plan()
        
        assert plan1.plan_id == plan2.plan_id
        assert plan1.checksum == plan2.checksum
        assert plan1.node_order == plan2.node_order
        assert plan1.groups == plan2.groups
    
    def test_deterministic_jitter(self):
        """Jitter must be deterministic."""
        j1 = DeterministicJitter.compute(attempt=1, execution_id="exec_123")
        j2 = DeterministicJitter.compute(attempt=1, execution_id="exec_123")
        assert j1 == j2
        
        j3 = DeterministicJitter.compute(attempt=2, execution_id="exec_123")
        assert j1 != j3
        
        j4 = DeterministicJitter.compute(attempt=1, execution_id="exec_456")
        assert j1 != j4
        
        assert 0 <= j1 <= 0.1
        assert 0 <= j3 <= 0.1
    

    def test_full_execution_deterministic(self):
        """Test full execution is deterministic."""
        async def run_test():
            dag = TypedDAG()
            
            async def runner1(inputs):
                return {"result": "value1"}
            
            async def runner2(inputs):
                return {"result": "value2"}
            
            dag.register_node(
                name="node1",
                engine="test",
                depends_on=[],
                input_types={},
                output_type=dict,
                runner=runner1
            )
            dag.register_node(
                name="node2",
                engine="test",
                depends_on=[Dependency("node1", DependencyType.HARD)],
                input_types={"node1": dict},
                output_type=dict,
                runner=runner2
            )
            
            result1 = await dag.execute()
            
            # Run again
            dag2 = TypedDAG()
            dag2.register_node(
                name="node1",
                engine="test",
                depends_on=[],
                input_types={},
                output_type=dict,
                runner=runner1
            )
            dag2.register_node(
                name="node2",
                engine="test",
                depends_on=[Dependency("node1", DependencyType.HARD)],
                input_types={"node1": dict},
                output_type=dict,
                runner=runner2
            )
            result2 = await dag2.execute()
            
            return result1, result2
        
        result1, result2 = asyncio.run(run_test())
        assert result1["status"] == "SUCCESS"
        assert result2["status"] == "SUCCESS"
        assert result1["plan_id"] == result2["plan_id"]
        assert result1["plan_checksum"] == result2["plan_checksum"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])