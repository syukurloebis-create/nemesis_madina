from enum import Enum


class EvidenceStatus(str, Enum):
    UPLOADED = "UPLOADED"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


class ConfidenceLevel(str, Enum):
    VERY_LOW = "VERY_LOW"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class CustodyAction(str, Enum):
    UPLOAD = "UPLOAD"
    VERIFY = "VERIFY"
    REVIEW = "REVIEW"
    EXPORT = "EXPORT"