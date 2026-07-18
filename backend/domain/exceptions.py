"""
NEMESIS Madina - Domain Exceptions
"""

class DomainException(Exception):
    """Base class for all domain exceptions."""
    pass


class InvalidCaseId(DomainException):
    """Raised when a CaseId is invalid."""
    pass


class InvalidConfidenceWeights(DomainException):
    """Raised when confidence weights are invalid."""
    pass


class InvalidFraudAnalysis(DomainException):
    """Raised when fraud analysis is invalid."""
    pass


class InvalidRiskAssessment(DomainException):
    """Raised when risk assessment is invalid."""
    pass


class InvalidEvidenceVerification(DomainException):
    """Raised when evidence verification is invalid."""
    pass


class InvalidGraphAnalysis(DomainException):
    """Raised when graph analysis is invalid."""
    pass


class InvalidProcurementAnalysis(DomainException):
    """Raised when procurement analysis is invalid."""
    pass


class AggregateNotFound(DomainException):
    """Raised when an aggregate is not found."""
    pass


class AggregateAlreadyExists(DomainException):
    """Raised when an aggregate already exists."""
    pass


class EventPublishingFailed(DomainException):
    """Raised when event publishing fails."""
    pass