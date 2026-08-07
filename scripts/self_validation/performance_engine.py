# performance_engine.py
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class PerformanceBudget:
    max_seconds: float
    mappers_count: int
    warning_threshold: float = 0.8  # 80% of max triggers warning

@dataclass
class PerformanceResult:
    execution_time: float
    mappers_count: int
    budget: Optional[PerformanceBudget]
    within_budget: bool
    below_warning: bool
    details: Dict[str, float]

class PerformanceEngine:
    """SLA-based performance monitoring."""
    
    DEFAULT_BUDGETS = {
        100: PerformanceBudget(max_seconds=2.0, mappers_count=100),
        500: PerformanceBudget(max_seconds=5.0, mappers_count=500),
        1000: PerformanceBudget(max_seconds=10.0, mappers_count=1000),
        2000: PerformanceBudget(max_seconds=20.0, mappers_count=2000),
        5000: PerformanceBudget(max_seconds=45.0, mappers_count=5000),
    }
    
    def __init__(self, budgets: Dict[int, PerformanceBudget] = None):
        self.budgets = budgets or self.DEFAULT_BUDGETS
    
    def get_budget(self, mappers_count: int) -> Optional[PerformanceBudget]:
        """Get performance budget for mapper count."""
        for count in sorted(self.budgets.keys()):
            if mappers_count <= count:
                return self.budgets[count]
        return None
    
    def measure(self, run_fn, mappers_count: int) -> PerformanceResult:
        """Measure execution time against budget."""
        budget = self.get_budget(mappers_count)
        
        start = time.perf_counter()
        result = run_fn()
        end = time.perf_counter()
        
        execution_time = end - start
        
        if budget:
            within_budget = execution_time <= budget.max_seconds
            below_warning = execution_time <= budget.max_seconds * budget.warning_threshold
        else:
            within_budget = True
            below_warning = True
        
        return PerformanceResult(
            execution_time=execution_time,
            mappers_count=mappers_count,
            budget=budget,
            within_budget=within_budget,
            below_warning=below_warning,
            details=result if isinstance(result, dict) else {}
        )