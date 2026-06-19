# backend/evidence/classification.py
from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime
from dataclasses import dataclass, field
import uuid


class EvidenceType(str, Enum):
    """Jenis evidence yang didukung"""
    DOCUMENT = "DOCUMENT"                 # Dokumen PDF, Word, Excel
    PHOTO = "PHOTO"                       # Foto/gambar
    VIDEO = "VIDEO"                       # Rekaman video
    INTERVIEW = "INTERVIEW"               # Hasil wawancara
    FINANCIAL_RECORD = "FINANCIAL_RECORD" # Data keuangan
    PROCUREMENT_RECORD = "PROCUREMENT_RECORD" # Data pengadaan
    EXTERNAL_INTELLIGENCE = "EXTERNAL_INTELLIGENCE" # Intelijen eksternal
    SYSTEM_LOG = "SYSTEM_LOG"             # Log sistem
    EMAIL = "EMAIL"                       # Email
    DATABASE_EXTRACT = "DATABASE_EXTRACT" # Ekstraksi database


class EvidenceSource(str, Enum):
    """Sumber evidence"""
    INTERNAL = "INTERNAL"                 # Dari internal Inspektorat
    EXTERNAL = "EXTERNAL"                 # Dari eksternal (vendor, OPD)
    THIRD_PARTY = "THIRD_PARTY"           # Dari pihak ketiga
    SYSTEM_GENERATED = "SYSTEM_GENERATED" # Dihasilkan sistem
    WHISTLEBLOWER = "WHISTLEBLOWER"       # Dari whistleblower


class EvidenceFormat(str, Enum):
    """Format file evidence"""
    PDF = "PDF"
    DOC = "DOC"
    DOCX = "DOCX"
    XLS = "XLS"
    XLSX = "XLSX"
    JPG = "JPG"
    PNG = "PNG"
    MP4 = "MP4"
    MP3 = "MP3"
    JSON = "JSON"
    CSV = "CSV"
    LOG = "LOG"
    OTHER = "OTHER"


class EvidenceClassificationLevel(str, Enum):
    """Level klasifikasi evidence"""
    PUBLIC = "PUBLIC"                     # Dapat diakses publik
    INTERNAL = "INTERNAL"                 # Internal Inspektorat
    CONFIDENTIAL = "CONFIDENTIAL"         # Rahasia
    RESTRICTED = "RESTRICTED"             # Sangat rahasia
    INVESTIGATION_ONLY = "INVESTIGATION_ONLY" # Hanya untuk investigasi


@dataclass
class EvidenceClassification:
    """Klasifikasi untuk evidence"""
    evidence_type: EvidenceType
    source_type: EvidenceSource
    format: EvidenceFormat
    classification_level: EvidenceClassificationLevel
    sensitivity_score: float = 0.5  # 0-1, higher = more sensitive
    requires_verification: bool = True
    requires_custody_chain: bool = True
    retention_base_days: int = 365 * 5  # 5 years default
    allowed_roles: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "evidence_type": self.evidence_type.value,
            "source_type": self.source_type.value,
            "format": self.format.value,
            "classification_level": self.classification_level.value,
            "sensitivity_score": self.sensitivity_score,
            "requires_verification": self.requires_verification,
            "requires_custody_chain": self.requires_custody_chain,
            "retention_base_days": self.retention_base_days,
            "allowed_roles": self.allowed_roles
        }


class EvidenceClassificationRegistry:
    """Registry untuk klasifikasi evidence"""
    
    def __init__(self):
        self._classifications: Dict[EvidenceType, EvidenceClassification] = {}
        self._init_registry()
    
    def _init_registry(self):
        """Initialize classification registry"""
        
        self._classifications[EvidenceType.DOCUMENT] = EvidenceClassification(
            evidence_type=EvidenceType.DOCUMENT,
            source_type=EvidenceSource.INTERNAL,
            format=EvidenceFormat.PDF,
            classification_level=EvidenceClassificationLevel.CONFIDENTIAL,
            sensitivity_score=0.6,
            requires_verification=True,
            requires_custody_chain=True,
            retention_base_days=365 * 10,  # 10 years
            allowed_roles=["INVESTIGATOR", "IRBAN", "INSPEKTUR"]
        )
        
        self._classifications[EvidenceType.FINANCIAL_RECORD] = EvidenceClassification(
            evidence_type=EvidenceType.FINANCIAL_RECORD,
            source_type=EvidenceSource.EXTERNAL,
            format=EvidenceFormat.XLSX,
            classification_level=EvidenceClassificationLevel.RESTRICTED,
            sensitivity_score=0.9,
            requires_verification=True,
            requires_custody_chain=True,
            retention_base_days=365 * 10,  # 10 years
            allowed_roles=["INVESTIGATOR", "IRBAN", "INSPEKTUR"]
        )
        
        self._classifications[EvidenceType.PROCUREMENT_RECORD] = EvidenceClassification(
            evidence_type=EvidenceType.PROCUREMENT_RECORD,
            source_type=EvidenceSource.EXTERNAL,
            format=EvidenceFormat.CSV,
            classification_level=EvidenceClassificationLevel.CONFIDENTIAL,
            sensitivity_score=0.7,
            requires_verification=True,
            requires_custody_chain=True,
            retention_base_days=365 * 5,  # 5 years
            allowed_roles=["INVESTIGATOR", "IRBAN"]
        )
        
        self._classifications[EvidenceType.INTERVIEW] = EvidenceClassification(
            evidence_type=EvidenceType.INTERVIEW,
            source_type=EvidenceSource.INTERNAL,
            format=EvidenceFormat.DOCX,
            classification_level=EvidenceClassificationLevel.RESTRICTED,
            sensitivity_score=0.85,
            requires_verification=True,
            requires_custody_chain=True,
            retention_base_days=365 * 10,  # 10 years
            allowed_roles=["INVESTIGATOR", "IRBAN", "INSPEKTUR"]
        )
        
        self._classifications[EvidenceType.PHOTO] = EvidenceClassification(
            evidence_type=EvidenceType.PHOTO,
            source_type=EvidenceSource.INTERNAL,
            format=EvidenceFormat.JPG,
            classification_level=EvidenceClassificationLevel.CONFIDENTIAL,
            sensitivity_score=0.5,
            requires_verification=True,
            requires_custody_chain=True,
            retention_base_days=365 * 5,
            allowed_roles=["INVESTIGATOR", "IRBAN", "INSPEKTUR"]
        )
        
        self._classifications[EvidenceType.VIDEO] = EvidenceClassification(
            evidence_type=EvidenceType.VIDEO,
            source_type=EvidenceSource.INTERNAL,
            format=EvidenceFormat.MP4,
            classification_level=EvidenceClassificationLevel.CONFIDENTIAL,
            sensitivity_score=0.7,
            requires_verification=True,
            requires_custody_chain=True,
            retention_base_days=365 * 5,
            allowed_roles=["INVESTIGATOR", "IRBAN", "INSPEKTUR"]
        )
        
        self._classifications[EvidenceType.EXTERNAL_INTELLIGENCE] = EvidenceClassification(
            evidence_type=EvidenceType.EXTERNAL_INTELLIGENCE,
            source_type=EvidenceSource.THIRD_PARTY,
            format=EvidenceFormat.OTHER,
            classification_level=EvidenceClassificationLevel.RESTRICTED,
            sensitivity_score=0.95,
            requires_verification=True,
            requires_custody_chain=True,
            retention_base_days=365 * 3,  # 3 years
            allowed_roles=["INSPEKTUR", "IRBAN"]
        )
        
        self._classifications[EvidenceType.SYSTEM_LOG] = EvidenceClassification(
            evidence_type=EvidenceType.SYSTEM_LOG,
            source_type=EvidenceSource.SYSTEM_GENERATED,
            format=EvidenceFormat.LOG,
            classification_level=EvidenceClassificationLevel.INTERNAL,
            sensitivity_score=0.3,
            requires_verification=False,
            requires_custody_chain=False,
            retention_base_days=365 * 2,  # 2 years
            allowed_roles=["INVESTIGATOR", "ADMIN"]
        )
        
        self._classifications[EvidenceType.EMAIL] = EvidenceClassification(
            evidence_type=EvidenceType.EMAIL,
            source_type=EvidenceSource.EXTERNAL,
            format=EvidenceFormat.OTHER,
            classification_level=EvidenceClassificationLevel.CONFIDENTIAL,
            sensitivity_score=0.75,
            requires_verification=True,
            requires_custody_chain=True,
            retention_base_days=365 * 5,
            allowed_roles=["INVESTIGATOR", "IRBAN"]
        )
        
        self._classifications[EvidenceType.DATABASE_EXTRACT] = EvidenceClassification(
            evidence_type=EvidenceType.DATABASE_EXTRACT,
            source_type=EvidenceSource.EXTERNAL,
            format=EvidenceFormat.JSON,
            classification_level=EvidenceClassificationLevel.RESTRICTED,
            sensitivity_score=0.85,
            requires_verification=True,
            requires_custody_chain=True,
            retention_base_days=365 * 5,
            allowed_roles=["INVESTIGATOR", "IRBAN", "INSPEKTUR"]
        )
    
    def get_classification(self, evidence_type: EvidenceType) -> Optional[EvidenceClassification]:
        """Get classification for evidence type"""
        return self._classifications.get(evidence_type)
    
    def get_all_classifications(self) -> List[EvidenceClassification]:
        """Get all classifications"""
        return list(self._classifications.values())
    
    def get_evidence_types(self) -> List[EvidenceType]:
        """Get all evidence types"""
        return list(self._classifications.keys())


# Singleton instance
_classification_registry = None

def get_classification_registry() -> EvidenceClassificationRegistry:
    """Get singleton classification registry"""
    global _classification_registry
    if _classification_registry is None:
        _classification_registry = EvidenceClassificationRegistry()
    return _classification_registry