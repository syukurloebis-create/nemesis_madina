"""
Custom exceptions for Control Plane
"""


class OrchestratorError(Exception):
    """Base orchestrator exception"""
    pass


class DuplicateJobError(OrchestratorError):
    """Job with same idempotency key already exists"""
    pass


class JobNotFoundError(OrchestratorError):
    """Job ID not found in registry"""
    pass


class ExecutionRejectedError(OrchestratorError):
    """Execution rejected by orchestrator (outside control plane)"""
    pass


class WatchdogTimeoutError(OrchestratorError):
    """Watchdog detected timeout/liveness issue"""
    pass


class RoutingError(OrchestratorError):
    """Event bus routing error"""
    pass