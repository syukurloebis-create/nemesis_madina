"""
Evidence Exceptions - Domain Specific Exceptions
"""


class EvidenceError(Exception):
    """Base exception for evidence domain"""
    pass


class EvidenceNotFoundError(EvidenceError):
    """Evidence not found in registry"""
    pass


class EvidenceHashMismatchError(EvidenceError):
    """Hash verification failed"""
    pass


class EvidenceCorruptedError(EvidenceError):
    """Evidence data is corrupted"""
    pass


class CustodyChainError(EvidenceError):
    """Custody chain validation failed"""
    pass


class EvidenceDuplicateError(EvidenceError):
    """Duplicate evidence detected"""
    pass
