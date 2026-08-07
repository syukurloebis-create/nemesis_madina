# tests/test_concurrency.py (FIXED)
import sys
import pytest
import asyncio
import time  
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from metadata_inventory.typed_dag import TypedDAG
from metadata_inventory.contracts import Dependency, DependencyType


class TestConcurrency:
    """Stress tests for concurrency."""
    
    def test_parallel_execution(self):
        """Test parallel execution of independent nodes."""
        async def run_parallel():
            dag = TypedDAG()
            
            async def create_runner(name: str):
                async def runner(inputs):
                    await asyncio.sleep(0.1)
                    return {"result": f"value_{name}", "node": name}
                return runner
            
            for i in range(10):
                runner = await create_runner(f"node{i}")
                dag.register_node(
                    name=f"node{i}",
                    engine="test",
                    depends_on=[],
                    input_types={},
                    output_type=dict,
                    runner=runner
                )
            
            start = time.perf_counter()
            result = await dag.execute()
            end = time.perf_counter()
            
            return result, end - start
        
        result, duration = asyncio.run(run_parallel())
        
        assert result["status"] == "SUCCESS"
        assert len(result["results"]) == 10
        assert duration < 0.5
    
    def test_dependency_chain(self):
        """Test deep dependency chain (sequential execution)."""
        async def run_chain():
            dag = TypedDAG()
            
            async def create_runner(name: str):
                async def runner(inputs):
                    await asyncio.sleep(0.05)
                    return {"result": f"value_{name}", "node": name}
                return runner
            
            prev = None
            for i in range(10):
                runner = await create_runner(f"node{i}")
                depends = []
                if prev is not None:
                    depends = [Dependency(prev, DependencyType.HARD)]
                dag.register_node(
                    name=f"node{i}",
                    engine="test",
                    depends_on=depends,
                    input_types={"node1": dict} if prev else {},
                    output_type=dict,
                    runner=runner
                )
                prev = f"node{i}"
            
            start = time.perf_counter()
            result = await dag.execute()
            end = time.perf_counter()
            
            return result, end - start
        
        result, duration = asyncio.run(run_chain())
        
        assert result["status"] == "SUCCESS"
        assert len(result["results"]) == 10
        assert 0.4 < duration < 1.0
    
    def test_diamond_dependency(self):
        """Test diamond dependency pattern."""
        async def run_diamond():
            dag = TypedDAG()
            
            async def create_runner(name: str, delay: float = 0.05):
                async def runner(inputs):
                    await asyncio.sleep(delay)
                    return {"result": f"value_{name}", "node": name}
                return runner
            
            runner_a = await create_runner("A", 0.05)
            dag.register_node(
                name="A",
                engine="test",
                depends_on=[],
                input_types={},
                output_type=dict,
                runner=runner_a
            )
            
            runner_b = await create_runner("B", 0.1)
            dag.register_node(
                name="B",
                engine="test",
                depends_on=[Dependency("A", DependencyType.HARD)],
                input_types={"A": dict},
                output_type=dict,
                runner=runner_b
            )
            
            runner_c = await create_runner("C", 0.1)
            dag.register_node(
                name="C",
                engine="test",
                depends_on=[Dependency("A", DependencyType.HARD)],
                input_types={"A": dict},
                output_type=dict,
                runner=runner_c
            )
            
            runner_d = await create_runner("D", 0.05)
            dag.register_node(
                name="D",
                engine="test",
                depends_on=[
                    Dependency("B", DependencyType.HARD),
                    Dependency("C", DependencyType.HARD)
                ],
                input_types={"B": dict, "C": dict},
                output_type=dict,
                runner=runner_d
            )
            
            start = time.perf_counter()
            result = await dag.execute()
            end = time.perf_counter()
            
            return result, end - start
        
        result, duration = asyncio.run(run_diamond())
        
        assert result["status"] == "SUCCESS"
        assert len(result["results"]) == 4
        assert 0.15 < duration < 0.5
    
    def test_high_throughput(self):
        """Test high throughput with many nodes."""
        async def run_throughput():
            dag = TypedDAG()
            
            async def create_runner(name: str):
                async def runner(inputs):
                    return {"result": f"value_{name}"}
                return runner
            
            for i in range(100):
                runner = await create_runner(f"node{i}")
                dag.register_node(
                    name=f"node{i}",
                    engine="test",
                    depends_on=[],
                    input_types={},
                    output_type=dict,
                    runner=runner
                )
            
            start = time.perf_counter()
            result = await dag.execute()
            end = time.perf_counter()
            
            return result, end - start
        
        result, duration = asyncio.run(run_throughput())
        
        assert result["status"] == "SUCCESS"
        assert len(result["results"]) == 100
        assert duration < 1.0
    
    def test_mixed_dependencies(self):
        """Test mixed hard/soft/optional dependencies."""
        async def run_mixed():
            dag = TypedDAG()
            
            async def create_runner(name: str):
                async def runner(inputs):
                    return {"result": f"value_{name}"}
                return runner
            
            runner_a = await create_runner("A")
            dag.register_node(
                name="A",
                engine="test",
                depends_on=[],
                input_types={},
                output_type=dict,
                runner=runner_a
            )
            
            runner_b = await create_runner("B")
            dag.register_node(
                name="B",
                engine="test",
                depends_on=[Dependency("A", DependencyType.HARD)],
                input_types={"A": dict},
                output_type=dict,
                runner=runner_b
            )
            
            runner_c = await create_runner("C")
            dag.register_node(
                name="C",
                engine="test",
                depends_on=[],
                input_types={},
                output_type=dict,
                runner=runner_c
            )
            
            runner_d = await create_runner("D")
            dag.register_node(
                name="D",
                engine="test",
                depends_on=[Dependency("C", DependencyType.SOFT)],
                input_types={"C": dict},
                output_type=dict,
                runner=runner_d
            )
            
            runner_e = await create_runner("E")
            dag.register_node(
                name="E",
                engine="test",
                depends_on=[],
                input_types={},
                output_type=dict,
                runner=runner_e
            )
            
            runner_f = await create_runner("F")
            dag.register_node(
                name="F",
                engine="test",
                depends_on=[Dependency("E", DependencyType.OPTIONAL)],
                input_types={"E": dict},
                output_type=dict,
                runner=runner_f
            )
            
            result = await dag.execute()
            return result
        
        result = asyncio.run(run_mixed())
        
        assert result["status"] == "SUCCESS"
        assert len(result["results"]) == 6
    
    def test_concurrent_safety(self):
        """Test concurrent execution safety with shared state."""
        async def run_concurrent():
            dag = TypedDAG()
        
            # Gunakan list sebagai shared state yang aman
            # Setiap node menambahkan hasilnya ke list
            results = []
        
            async def create_runner(name: str):
                async def runner(inputs):
                    # Simulasi work
                    await asyncio.sleep(0.001)
                    # Append ke list (thread-safe dalam asyncio)
                    results.append(name)
                    return {"result": f"value_{name}"}
                return runner
        
            for i in range(20):
                runner = await create_runner(f"node{i}")
                dag.register_node(
                    name=f"node{i}",
                    engine="test",
                    depends_on=[],
                    input_types={},
                    output_type=dict,
                    runner=runner
                )
        
            result = await dag.execute()
            return result, len(results)
    
        result, final_count = asyncio.run(run_concurrent())
    
        assert result["status"] == "SUCCESS"
        assert final_count == 20  # Semua 20 node harus selesai
        assert len(result["results"]) == 20  # Semua 20 hasil harus ada


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])