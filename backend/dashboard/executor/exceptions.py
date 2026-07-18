# backend/dashboard/executor/exceptions.py

class ExecutionFailedException(Exception):
    """Raised when a required task fails."""
    pass

class CircuitOpenException(Exception):
    """Raised when circuit breaker is open."""
    pass


# In ParallelExecutor
if failed_required:
    raise ExecutionFailedException(
        f"Required tasks failed: {', '.join(errors)}"
    )