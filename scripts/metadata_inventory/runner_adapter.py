"""
Runner Adapter - Converts typed results to artifacts.
Phase 1 - Core Infrastructure
"""

from typing import Dict, List, Optional, Any, Callable, Type 
from dataclasses import is_dataclass, asdict

from .contracts import ArtifactEnvelope
from .artifact_factory import ArtifactFactory


class RunnerAdapter:
    """Adapter that wraps a runner to produce ArtifactEnvelope."""
    
    @staticmethod
    def wrap(
        runner: Callable[[Dict[str, Any]], Any],
        artifact_name: str,
        output_type: Type,
        schema_version: str = "1.0"
    ) -> Callable[[Dict[str, Any]], ArtifactEnvelope]:
        """Wrap a runner to produce ArtifactEnvelope."""
        async def wrapped(inputs: Dict[str, Any]) -> ArtifactEnvelope:
            result = await runner(inputs)
            
            if not isinstance(result, output_type):
                raise TypeError(
                    f"Runner returned {type(result)}, expected {output_type}"
                )
            
            if is_dataclass(result):
                payload = {
                    k: v for k, v in asdict(result).items()
                    if not k.startswith('_')
                }
            elif isinstance(result, dict):
                payload = result
            else:
                payload = {"value": result}
            
            return ArtifactFactory.create(
                name=artifact_name,
                payload=payload,
                producer=artifact_name,
                schema_version=schema_version
            )
        
        return wrapped