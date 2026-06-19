#!/usr/bin/env python3
"""
NEMESIS FASE 2 - Restructure Core Layer
Memisahkan core business logic dari infrastructure
"""

import sys
import shutil
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

CORE_DIR = PROJECT_ROOT / "backend" / "core"
ENTITIES_DIR = CORE_DIR / "entities"
SERVICES_DIR = CORE_DIR / "services"
PORTS_DIR = CORE_DIR / "ports"

def create_core_structure():
    """Buat struktur core yang terorganisir"""
    print("\n[DIR] Creating core structure...")
    
    ENTITIES_DIR.mkdir(parents=True, exist_ok=True)
    SERVICES_DIR.mkdir(parents=True, exist_ok=True)
    PORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    return True

def create_entities():
    """Buat entities.py - domain entities"""
    content = '''"""
Core Entities - Domain Entities
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum


class EntityStatus(str, Enum):
    """Entity status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    DELETED = "deleted"


@dataclass
class BaseEntity:
    """Base entity with common fields"""
    id: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    status: EntityStatus = EntityStatus.ACTIVE
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "status": self.status.value
        }


@dataclass
class AnalysisResult(BaseEntity):
    """Analysis result entity"""
    entity_id: str
    analysis_type: str
    score: float
    confidence: float
    details: Dict[str, Any] = field(default_factory=dict)
    explanation: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "entity_id": self.entity_id,
            "analysis_type": self.analysis_type,
            "score": self.score,
            "confidence": self.confidence,
            "details": self.details,
            "explanation": self.explanation
        })
        return data


@dataclass
class AnomalyReport(BaseEntity):
    """Anomaly report entity"""
    source: str
    severity: str  # low, medium, high, critical
    description: str
    evidence_ids: List[str] = field(default_factory=list)
    resolved: bool = False
    resolution_note: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "source": self.source,
            "severity": self.severity,
            "description": self.description,
            "evidence_ids": self.evidence_ids,
            "resolved": self.resolved,
            "resolution_note": self.resolution_note
        })
        return data
'''
    
    file_path = ENTITIES_DIR / "entities.py"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def create_services():
    """Buat services.py - business services"""
    content = '''"""
Core Services - Business Logic Services
"""

from typing import List, Dict, Any, Optional
from datetime import datetime

from backend.core.entities.entities import AnalysisResult, AnomalyReport


class AnalysisService:
    """Service for performing analysis"""
    
    def __init__(self):
        self._results: List[AnalysisResult] = []
    
    def record_result(
        self,
        entity_id: str,
        analysis_type: str,
        score: float,
        confidence: float,
        details: Dict[str, Any] = None,
        explanation: str = None
    ) -> AnalysisResult:
        """Record analysis result"""
        result = AnalysisResult(
            id=f"result_{len(self._results) + 1}",
            entity_id=entity_id,
            analysis_type=analysis_type,
            score=score,
            confidence=confidence,
            details=details or {},
            explanation=explanation
        )
        self._results.append(result)
        return result
    
    def get_results_for_entity(self, entity_id: str) -> List[AnalysisResult]:
        """Get all results for an entity"""
        return [r for r in self._results if r.entity_id == entity_id]
    
    def get_latest_result(self, entity_id: str, analysis_type: str) -> Optional[AnalysisResult]:
        """Get latest result for entity and type"""
        results = [
            r for r in self._results 
            if r.entity_id == entity_id and r.analysis_type == analysis_type
        ]
        if results:
            return max(results, key=lambda x: x.created_at)
        return None


class AnomalyService:
    """Service for anomaly detection and reporting"""
    
    def __init__(self):
        self._reports: List[AnomalyReport] = []
    
    def create_report(
        self,
        source: str,
        severity: str,
        description: str,
        evidence_ids: List[str] = None
    ) -> AnomalyReport:
        """Create anomaly report"""
        report = AnomalyReport(
            id=f"anomaly_{len(self._reports) + 1}",
            source=source,
            severity=severity,
            description=description,
            evidence_ids=evidence_ids or []
        )
        self._reports.append(report)
        return report
    
    def resolve_report(self, report_id: str, resolution_note: str) -> bool:
        """Mark report as resolved"""
        for report in self._reports:
            if report.id == report_id:
                report.resolved = True
                report.resolution_note = resolution_note
                report.updated_at = datetime.now()
                return True
        return False
    
    def get_active_reports(self) -> List[AnomalyReport]:
        """Get unresolved reports"""
        return [r for r in self._reports if not r.resolved]
    
    def get_reports_by_severity(self, severity: str) -> List[AnomalyReport]:
        """Get reports by severity"""
        return [r for r in self._reports if r.severity == severity]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get anomaly statistics"""
        return {
            "total_reports": len(self._reports),
            "active_reports": len(self.get_active_reports()),
            "resolved_reports": len([r for r in self._reports if r.resolved]),
            "by_severity": {
                severity: len([r for r in self._reports if r.severity == severity])
                for severity in ["low", "medium", "high", "critical"]
            }
        }
'''
    
    file_path = SERVICES_DIR / "services.py"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def create_ports():
    """Buat ports.py - abstract interfaces"""
    content = '''"""
Core Ports - Abstract Interfaces for Dependency Inversion
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime


class EvidenceRepositoryPort(ABC):
    """Port for evidence storage"""
    
    @abstractmethod
    def save(self, evidence: Dict[str, Any]) -> str:
        """Save evidence and return ID"""
        pass
    
    @abstractmethod
    def get(self, evidence_id: str) -> Optional[Dict[str, Any]]:
        """Get evidence by ID"""
        pass
    
    @abstractmethod
    def list_all(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """List all evidence"""
        pass
    
    @abstractmethod
    def delete(self, evidence_id: str) -> bool:
        """Delete evidence"""
        pass


class EventBusPort(ABC):
    """Port for event publishing"""
    
    @abstractmethod
    async def publish(self, event_type: str, data: Any, source: str) -> str:
        """Publish event and return event ID"""
        pass
    
    @abstractmethod
    def subscribe(self, event_type: str, handler: callable):
        """Subscribe to events"""
        pass


class GraphRepositoryPort(ABC):
    """Port for graph storage"""
    
    @abstractmethod
    def add_node(self, node_id: str, label: str, properties: Dict[str, Any]) -> bool:
        """Add node to graph"""
        pass
    
    @abstractmethod
    def add_edge(self, source: str, target: str, label: str, weight: float) -> bool:
        """Add edge to graph"""
        pass
    
    @abstractmethod
    def get_neighbors(self, node_id: str) -> List[str]:
        """Get neighbors of node"""
        pass


class CachePort(ABC):
    """Port for caching"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int = 3600):
        """Set value in cache"""
        pass
    
    @abstractmethod
    async def delete(self, key: str):
        """Delete from cache"""
        pass
'''
    
    file_path = PORTS_DIR / "ports.py"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def create_core_init():
    """Buat __init__.py untuk core"""
    content = '''"""
NEMESIS Core Layer - Business Logic
"""

from backend.core.entities.entities import (
    BaseEntity, EntityStatus, AnalysisResult, AnomalyReport
)
from backend.core.services.services import AnalysisService, AnomalyService
from backend.core.ports.ports import (
    EvidenceRepositoryPort, EventBusPort, GraphRepositoryPort, CachePort
)

__all__ = [
    'BaseEntity',
    'EntityStatus', 
    'AnalysisResult',
    'AnomalyReport',
    'AnalysisService',
    'AnomalyService',
    'EvidenceRepositoryPort',
    'EventBusPort',
    'GraphRepositoryPort',
    'CachePort'
]
'''
    
    file_path = CORE_DIR / "__init__.py"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def main():
    """Main execution"""
    print("\n" + "="*60)
    print("FASE 2: RESTRUCTURE CORE LAYER")
    print("="*60)
    
    success = True
    success &= create_core_structure()
    success &= create_entities()
    success &= create_services()
    success &= create_ports()
    success &= create_core_init()
    
    print("\n" + "="*60)
    if success:
        print("[OK] CORE LAYER RESTRUCTURED")
        print(f"   Entities: {ENTITIES_DIR}")
        print(f"   Services: {SERVICES_DIR}")
        print(f"   Ports: {PORTS_DIR}")
    else:
        print("[ERR] CORE LAYER RESTRUCTURE FAILED")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())