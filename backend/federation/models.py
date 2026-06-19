"""Federated Governance Models - Multi-tenant and cross-institution governance"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4
from enum import Enum
from pydantic import BaseModel, Field


class InstitutionType(str, Enum):
    KEMENPAN = "kemenpan"
    BPKP = "bpkp"
    BPK = "bpk"
    INSPEKTORAT = "inspektorat"
    APIP = "apip"
    KPK = "kpk"
    KEJAKSAAN = "kejaksaan"
    POLRI = "polri"


class DataClassification(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    SECRET = "secret"


class FederationTenant(BaseModel):
    tenant_id: UUID = Field(default_factory=uuid4)
    institution_name: str
    institution_type: InstitutionType
    region: Optional[str] = None
    level: str = "kabupaten"  # kabupaten, provinsi, nasional
    api_key: str
    is_active: bool = True
    quota_limit: int = 10000
    quota_used: int = 0
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class FederationDataShare(BaseModel):
    share_id: UUID = Field(default_factory=uuid4)
    source_tenant_id: UUID
    target_tenant_id: UUID
    data_type: str  # anomaly, case, evidence, decision
    data_id: UUID
    classification: DataClassification
    shared_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CrossTenantQuery(BaseModel):
    query_id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID
    query_type: str
    parameters: Dict[str, Any]
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class NationalRiskRegistry(BaseModel):
    registry_id: UUID = Field(default_factory=uuid4)
    entity_id: str
    entity_type: str
    risk_score: float
    confidence: float
    source_tenants: List[UUID]
    reported_at: datetime = Field(default_factory=datetime.now)
    status: str = "active"
    metadata: Dict[str, Any] = Field(default_factory=dict)
