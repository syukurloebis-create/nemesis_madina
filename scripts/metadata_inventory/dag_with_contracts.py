# dag_with_contracts.py
from typing import Dict, List, Optional, Any, Callable, Type
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import hashlib

from contracts import ArtifactStore

class DependencyType(Enum):
    HARD = "hard"      # Must succeed for downstream to run
    SOFT = "soft"      # Can continue but with degraded state
    OPTIONAL = "optional"  # Can skip if not available

@dataclass
class Dependency:
    name: str
    type: DependencyType = DependencyType.HARD

@dataclass
class DAGNode:
    name: str
    engine: str
    depends_on: List[Dependency]
    input_types: Dict[str, Type]  # Artifact name -> expected type
    output_type: Type  # Expected output type
    run: Callable
    status: str = "pending"  # pending, running, completed, failed, skipped
    result: Any = None
    retry_count: int = 0
    max_retries: int = 3
    timeout_seconds: float = 30.0

class ArtifactDAG:
    """DAG with typed contracts and failure propagation."""
    
    def __init__(self):
        self.nodes: Dict[str, DAGNode] = {}
        self.artifact_store = ArtifactStore()
        self.results: Dict[str, Any] = {}
    
    def add_node(self, name: str, engine: str, depends_on: List[Dependency],
                 input_types: Dict[str, Type], output_type: Type,
                 run: Callable, max_retries: int = 3, timeout_seconds: float = 30.0) -> None:
        """Add a node with typed contracts."""
        self.nodes[name] = DAGNode(
            name=name,
            engine=engine,
            depends_on=depends_on,
            input_types=input_types,
            output_type=output_type,
            run=run,
            max_retries=max_retries,
            timeout_seconds=timeout_seconds
        )
    
    def validate_contracts(self) -> List[str]:
        """Validate all input/output contracts."""
        errors = []
        
        for name, node in self.nodes.items():
            for dep in node.depends_on:
                if dep.name not in self.nodes:
                    errors.append(f"Node '{name}' depends on unknown node '{dep.name}'")
                
                # Check if input artifact is available
                expected_type = node.input_types.get(dep.name)
                if expected_type:
                    # Check if upstream output matches expected type
                    upstream = self.nodes.get(dep.name)
                    if upstream and upstream.output_type != expected_type:
                        errors.append(
                            f"Node '{name}' expects {expected_type} from '{dep.name}', "
                            f"but '{dep.name}' produces {upstream.output_type}"
                        )
        
        return errors
    
    def get_execution_plan(self) -> Dict[str, Any]:
        """Get execution plan with dependency resolution."""
        plan = {
            "groups": [],
            "failures": [],
            "skips": []
        }
        
        # Get all nodes
        pending = set(self.nodes.keys())
        completed = set()
        groups = []
        
        while pending:
            group = []
            for node_name in pending:
                deps = [d.name for d in self.nodes[node_name].depends_on]
                if all(d in completed for d in deps):
                    group.append(node_name)
            
            if not group:
                # Remaining nodes have unmet dependencies
                # Check if any are due to failures
                for node_name in pending:
                    deps = [d.name for d in self.nodes[node_name].depends_on]
                    failed_deps = [d for d in deps if d not in completed and d not in pending]
                    if failed_deps:
                        node = self.nodes[node_name]
                        # Check if any failed deps are hard dependencies
                        hard_fail = False
                        for dep in node.depends_on:
                            if dep.name in failed_deps and dep.type == DependencyType.HARD:
                                hard_fail = True
                                break
                        if hard_fail:
                            plan["failures"].append({
                                "node": node_name,
                                "reason": f"Hard dependency failed: {failed_deps}"
                            })
                        else:
                            plan["skips"].append(node_name)
                break
            
            groups.append(group)
            pending -= set(group)
            completed.update(group)
        
        plan["groups"] = groups
        return plan
    
    async def execute_node(self, node: DAGNode) -> Any:
        """Execute a single node with retry and timeout."""
        for attempt in range(node.max_retries + 1):
            try:
                node.status = "running"
                # Get input artifacts
                inputs = {}
                for dep in node.depends_on:
                    artifact = self.artifact_store.get(dep.name)
                    inputs[dep.name] = artifact
                
                # Execute with timeout
                result = await asyncio.wait_for(
                    node.run(inputs),
                    timeout=node.timeout_seconds
                )
                
                # Validate output type
                if result is not None and not isinstance(result, node.output_type):
                    raise TypeError(f"Node {node.name} returned {type(result)}, expected {node.output_type}")
                
                # Store artifact
                self.artifact_store.put(node.name, result)
                node.result = result
                node.status = "completed"
                return result
                
            except asyncio.TimeoutError:
                if attempt == node.max_retries:
                    node.status = "failed"
                    raise TimeoutError(f"Node {node.name} timed out after {node.timeout_seconds}s")
                # Retry
                continue
            except Exception as e:
                if attempt == node.max_retries:
                    node.status = "failed"
                    raise
                # Retry with backoff
                await asyncio.sleep(2 ** attempt)
                continue
        
        node.status = "failed"
        return None
    
    async def execute(self) -> Dict[str, Any]:
        """Execute the DAG with failure propagation."""
        # Validate contracts
        errors = self.validate_contracts()
        if errors:
            return {"status": "ERROR", "errors": errors}
        
        # Get execution plan
        plan = self.get_execution_plan()
        results = {}
        
        # Execute groups
        for group in plan["groups"]:
            tasks = []
            for node_name in group:
                node = self.nodes[node_name]
                task = asyncio.create_task(self.execute_node(node))
                tasks.append((node_name, task))
            
            # Wait for all tasks in group
            for node_name, task in tasks:
                try:
                    results[node_name] = await task
                except Exception as e:
                    results[node_name] = {"error": str(e), "node": node_name}
        
        # Handle failures and skips
        for failure in plan["failures"]:
            results[failure["node"]] = {"error": failure["reason"], "node": failure["node"], "skipped": True}
            self.nodes[failure["node"]].status = "skipped"
        
        for skip in plan["skips"]:
            results[skip] = {"skipped": True, "node": skip}
            self.nodes[skip].status = "skipped"
        
        return results
    
    def get_status_report(self) -> Dict[str, str]:
        """Get status report for all nodes."""
        return {name: node.status for name, node in self.nodes.items()}