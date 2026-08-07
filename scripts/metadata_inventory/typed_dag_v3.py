# typed_dag_v3.py
"""
Typed DAG v3 - With full abstractions and contract verification.
Phase 1.6 - Contract Enforcement & Abstraction
"""

import asyncio
from typing import Dict, List, Optional, Any, Callable, Type, Tuple
from datetime import datetime

from contracts import (
    ArtifactId, ArtifactEnvelope, NodeDefinition,
    Dependency, DependencyType, ExecutionRecord
)
from execution_plan import ExecutionPlanner
from execution_sink_interface import ExecutionSink, MemoryExecutionSink
from artifact_store_interface import ArtifactStore, InMemoryArtifactStore
from runner_adapter import RunnerAdapter
from retry_policy import RetryPolicy, RetryStrategy
from deterministic_jitter import DeterministicJitter
from contract_verifier import ContractVerifier
from artifact_identity import ExecutionMetadata


class TypedDAG:
    """
    Typed DAG with full abstractions and contract verification.
    """
    
    def __init__(
        self,
        store: Optional[ArtifactStore] = None,
        sink: Optional[ExecutionSink] = None
    ):
        self._nodes: Dict[str, NodeDefinition] = {}
        self._runners: Dict[str, Callable] = {}
        self._store = store or InMemoryArtifactStore()
        self._sink = sink or MemoryExecutionSink()
        self._execution_id = 0
        self._verifier = ContractVerifier()
        self._plan: Optional['ExecutionPlan'] = None
    
    def register_node(
        self,
        name: str,
        engine: str,
        depends_on: List[Dependency],
        input_types: Dict[str, Type],
        output_type: Type,
        runner: Callable,
        max_retries: int = 3,
        timeout_seconds: float = 30.0,
        retry_strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    ) -> List['ContractViolation']:
        """Register a node with a runner."""
        # Verify contracts before registration
        violations = self._verifier.verify_node(
            node_name=name,
            depends_on=depends_on,
            input_types=input_types,
            output_type=output_type,
            runner=runner
        )
        
        if any(v.severity == "ERROR" for v in violations):
            return violations
        
        # Wrap runner to produce artifact
        wrapped_runner = RunnerAdapter.wrap(
            runner=runner,
            artifact_name=name,
            output_type=output_type
        )
        
        definition = NodeDefinition(
            name=name,
            engine=engine,
            depends_on=depends_on,
            input_types=input_types,
            output_type=output_type,
            max_retries=max_retries,
            timeout_seconds=timeout_seconds,
            retry_policy=retry_strategy.value
        )
        self._nodes[name] = definition
        self._runners[name] = wrapped_runner
        
        # Invalidate plan
        self._plan = None
        
        return violations
    
    def validate(self) -> Dict[str, Any]:
        """Validate the DAG with contract verification."""
        violations = self._verifier.verify_all(self._nodes, self._runners)
        
        errors = []
        warnings = []
        
        for node, v in violations.items():
            for violation in v:
                if violation.severity == "ERROR":
                    errors.append(f"{node}: {violation.message}")
                else:
                    warnings.append(f"{node}: {violation.message}")
        
        # Build plan if valid
        plan = None
        if not errors:
            planner = ExecutionPlanner(self._nodes)
            plan = planner.plan()
            self._plan = plan
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "plan": plan,
            "violations": violations
        }
    
    async def _execute_node(self, node_name: str) -> Tuple[str, Optional[ArtifactEnvelope], Optional[str]]:
        """Execute a single node."""
        if node_name not in self._runners:
            return node_name, None, f"No runner for node {node_name}"
        
        node = self._nodes[node_name]
        runner = self._runners[node_name]
        retry_policy = RetryPolicy(
            strategy=RetryStrategy(node.retry_policy),
            max_retries=node.max_retries
        )
        
        # Get input artifacts
        inputs = {}
        for dep in node.depends_on:
            artifact = self._store.get_latest(dep.node_name)
            if artifact:
                inputs[dep.node_name] = artifact
            elif dep.dependency_type == DependencyType.HARD:
                return node_name, None, f"Required artifact {dep.node_name} not available"
        
        # Generate execution ID
        execution_id = f"exec_{self._execution_id}"
        self._execution_id += 1
        
        # Log start
        started_at = datetime.now()
        self._sink.log_start(node_name, execution_id, [a.artifact_id for a in inputs.values()])
        
        # Execute with retry
        for attempt in range(node.max_retries + 1):
            try:
                # Calculate deterministic jitter
                jitter = DeterministicJitter.compute(attempt, execution_id)
                
                # Execute with timeout
                artifact = await asyncio.wait_for(
                    runner(inputs),
                    timeout=node.timeout_seconds
                )
                
                completed_at = datetime.now()
                
                # Validate artifact
                if not isinstance(artifact, ArtifactEnvelope):
                    return node_name, None, f"Runner returned {type(artifact)}, expected ArtifactEnvelope"
                
                if not artifact.verify():
                    return node_name, None, "Artifact checksum verification failed"
                
                # Append to store
                self._store.append(artifact)
                
                # Log completion
                self._sink.log_completion(
                    node_name=node_name,
                    execution_id=execution_id,
                    started_at=started_at.isoformat(),
                    completed_at=completed_at.isoformat(),
                    status="COMPLETED",
                    input_artifacts=[a.artifact_id for a in inputs.values()],
                    output_artifact=artifact.artifact_id,
                    artifact_checksum=artifact.checksum,
                    retry_count=attempt
                )
                
                return node_name, artifact, None
                
            except asyncio.TimeoutError:
                if not retry_policy.should_retry(attempt, TimeoutError()):
                    self._sink.log_completion(
                        node_name=node_name,
                        execution_id=execution_id,
                        started_at=started_at.isoformat(),
                        completed_at=datetime.now().isoformat(),
                        status="FAILED",
                        input_artifacts=[a.artifact_id for a in inputs.values()],
                        error=f"Timeout after {attempt+1} attempts",
                        retry_count=attempt
                    )
                    return node_name, None, f"Timeout after {attempt+1} attempts"
                
                delay = retry_policy.get_delay(attempt) + jitter
                await asyncio.sleep(delay)
                
            except Exception as e:
                if not retry_policy.should_retry(attempt, e):
                    self._sink.log_completion(
                        node_name=node_name,
                        execution_id=execution_id,
                        started_at=started_at.isoformat(),
                        completed_at=datetime.now().isoformat(),
                        status="FAILED",
                        input_artifacts=[a.artifact_id for a in inputs.values()],
                        error=str(e),
                        retry_count=attempt
                    )
                    return node_name, None, str(e)
                
                delay = retry_policy.get_delay(attempt) + jitter
                await asyncio.sleep(delay)
        
        return node_name, None, "Max retries exhausted"
    
    async def execute(self) -> Dict[str, Any]:
        """Execute the entire DAG."""
        # Validate first
        validation = self.validate()
        if not validation["valid"]:
            return {"status": "ERROR", "errors": validation["errors"]}
        
        # Get execution plan (immutable snapshot)
        plan = self._plan
        if plan is None:
            planner = ExecutionPlanner(self._nodes)
            plan = planner.plan()
            self._plan = plan
        
        # Execute groups
        results = {}
        for group in plan.groups:
            tasks = [self._execute_node(node_name) for node_name in group]
            group_results = await asyncio.gather(*tasks)
            
            for node_name, artifact, error in group_results:
                if error:
                    results[node_name] = {"status": "FAILED", "error": error}
                else:
                    results[node_name] = {
                        "status": "COMPLETED",
                        "artifact_id": artifact.artifact_id.value if artifact else None,
                        "artifact_checksum": artifact.checksum if artifact else None
                    }
        
        return {
            "status": "SUCCESS",
            "plan_id": plan.plan_id,
            "plan_checksum": plan.checksum,
            "results": results,
            "artifact_count": len(self._store.get_append_log()),
            "execution_count": len(self._sink.get_entries()),
            "sink_verified": self._sink.verify()
        }
    
    def get_store(self) -> ArtifactStore:
        return self._store
    
    def get_sink(self) -> ExecutionSink:
        return self._sink
    
    def get_plan(self) -> Optional['ExecutionPlan']:
        return self._plan