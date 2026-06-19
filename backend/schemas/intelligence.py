# schemas/intelligence.py - Intelligence Response Models
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class RiskComponents(BaseModel):
    """Risk components breakdown"""
    case_risk: float = Field(..., description="Risk from case data (0-100)")
    graph_risk: float = Field(..., description="Risk from graph analysis (0-100)")
    fraud_score: float = Field(..., description="Risk from ML fraud detection (0-100)")
    evidence_trust: float = Field(..., description="Risk from evidence trust (0-100)")
    
    class Config:
        schema_extra = {
            "example": {
                "case_risk": 80.0,
                "graph_risk": 16.0,
                "fraud_score": 85.0,
                "evidence_trust": 70.0
            }
        }

class GraphRiskResponse(BaseModel):
    """Graph risk analysis response"""
    graph_risk: float = Field(..., description="Graph-based risk score (0-100)")
    level: str = Field(..., description="Risk level: HIGH/MEDIUM/LOW/NO_DATA")
    entities: int = Field(..., description="Number of entities in graph")
    edges: int = Field(..., description="Number of relationships in graph")
    confidence: int = Field(..., description="Confidence level (0-100)")
    data_source: str = Field(..., description="Data source: exact_match/fallback/none")
    
    class Config:
        schema_extra = {
            "example": {
                "graph_risk": 16.0,
                "level": "LOW",
                "entities": 549,
                "edges": 4,
                "confidence": 70,
                "data_source": "exact_match"
            }
        }

class IntelligenceScoreResponse(BaseModel):
    """Standard intelligence score response"""
    case_id: str = Field(..., description="Case identifier")
    risk_score: float = Field(..., description="Overall risk score (0-100)")
    risk_level: str = Field(..., description="Risk level: HIGH/MEDIUM/LOW")
    components: RiskComponents = Field(..., description="Detailed risk components")
    timestamp: datetime = Field(default_factory=datetime.now)
    version: str = Field(default="v1.0")
    
    class Config:
        schema_extra = {
            "example": {
                "case_id": "446e216d-eb0e-487e-8e6b-ec943468ea20",
                "risk_score": 61.0,
                "risk_level": "HIGH",
                "components": {
                    "case_risk": 80.0,
                    "graph_risk": 16.0,
                    "fraud_score": 85.0,
                    "evidence_trust": 70.0
                },
                "timestamp": "2026-06-19T15:06:57.086289",
                "version": "v1.0"
            }
        }
