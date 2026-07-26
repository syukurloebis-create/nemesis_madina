# scripts/pipeline/plugin.py
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class IPipelineStage(ABC):
    """Interface for pipeline stage plugins"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Stage name"""
        pass
    
    @property
    @abstractmethod
    def stage_type(self) -> str:
        """Stage type (scan, normalize, validate, generate, gate)"""
        pass
    
    @property
    @abstractmethod
    def dependencies(self) -> list:
        """Dependencies (stage names)"""
        pass
    
    @abstractmethod
    def execute(self, context: ArchitectureContext) -> ArchitectureContext:
        """Execute the stage"""
        pass
    
    @abstractmethod
    def validate(self, context: ArchitectureContext) -> bool:
        """Validate stage prerequisites"""
        pass

class PipelinePluginManager:
    """Manage pipeline plugins"""
    
    def __init__(self):
        self.plugins: Dict[str, IPipelineStage] = {}
        self.stage_order: List[str] = []
    
    def register(self, plugin: IPipelineStage):
        """Register a pipeline plugin"""
        self.plugins[plugin.name] = plugin
        self._update_order()
    
    def _update_order(self):
        """Update execution order based on dependencies"""
        # Topological sort of stages
        graph = {}
        for name, plugin in self.plugins.items():
            graph[name] = plugin.dependencies
        
        # Kahn's algorithm
        in_degree = {node: 0 for node in graph}
        for node, deps in graph.items():
            for dep in deps:
                if dep in in_degree:
                    in_degree[dep] += 1
        
        queue = [n for n in graph if in_degree[n] == 0]
        order = []
        
        while queue:
            node = queue.pop(0)
            order.append(node)
            for dep in graph[node]:
                in_degree[dep] -= 1
                if in_degree[dep] == 0:
                    queue.append(dep)
        
        self.stage_order = order
    
    def execute(self, context: ArchitectureContext, 
                from_stage: Optional[str] = None,
                to_stage: Optional[str] = None) -> ArchitectureContext:
        """Execute pipeline stages"""
        start_idx = self.stage_order.index(from_stage) if from_stage else 0
        end_idx = self.stage_order.index(to_stage) if to_stage else len(self.stage_order) - 1
        
        for stage_name in self.stage_order[start_idx:end_idx + 1]:
            plugin = self.plugins[stage_name]
            
            # Validate
            if not plugin.validate(context):
                raise ValueError(f"Stage {stage_name} validation failed")
            
            # Execute
            context.log.info(f"🚀 Executing stage: {stage_name}")
            context = plugin.execute(context)
            context.log.info(f"✅ Completed stage: {stage_name}")
        
        return context

# Example: Custom Security Scan Stage
class SecurityScanStage(IPipelineStage):
    @property
    def name(self) -> str:
        return "security_scan"
    
    @property
    def stage_type(self) -> str:
        return "scan"
    
    @property
    def dependencies(self) -> list:
        return ["inventory"]
    
    def execute(self, context: ArchitectureContext) -> ArchitectureContext:
        # Run security scan on modules
        context.security = self._run_security_scan(context.inventory)
        return context
    
    def validate(self, context: ArchitectureContext) -> bool:
        return context.inventory is not None