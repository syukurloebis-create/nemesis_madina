"""
Explainable Risk Metrics untuk NEMESIS V8+
Menyediakan faktor-faktor yang berkontribusi pada skor risiko
"""

from prometheus_client import Gauge, Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST, CollectorRegistry
from fastapi import APIRouter, Response, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import logging
from datetime import datetime
import random
import math

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/risk-metrics", tags=["risk_metrics"])

# Registry untuk risk metrics
risk_registry = CollectorRegistry()

# ============================================
# RISK METRICS
# ============================================

# Overall risk score per entity
entity_risk_score = Gauge(
    "risk_entity_score",
    "Current risk score for entity (0-100)",
    ["entity_id", "entity_name", "entity_type"],
    registry=risk_registry
)

# Risk distribution
risk_distribution = Gauge(
    "risk_distribution_count",
    "Number of entities in each risk level",
    ["risk_level"],  # critical, high, medium, low
    registry=risk_registry
)

# Average risk score across all entities
avg_risk_score = Gauge(
    "risk_average_score",
    "Average risk score across all entities",
    registry=risk_registry
)

# ============================================
# CONTRIBUTING FACTORS METRICS
# ============================================

# Contributing factors for risk score
risk_contributing_factor = Gauge(
    "risk_contributing_factor_weight",
    "Weight of contributing factor for entity risk",
    ["entity_id", "factor_name"],
    registry=risk_registry
)

# Anomaly count per factor type
anomaly_count_by_factor = Gauge(
    "anomaly_count_by_factor",
    "Number of anomalies detected by factor type",
    ["factor_type", "severity"],
    registry=risk_registry
)

# ============================================
# TREND METRICS
# ============================================

# Risk trend over time (stored as series)
risk_trend_value = Gauge(
    "risk_trend_value",
    "Risk score over time",
    ["entity_id", "time_bucket"],
    registry=risk_registry
)

# ============================================
# CONFIDENCE METRICS
# ============================================

# AI confidence score per prediction
prediction_confidence = Gauge(
    "risk_prediction_confidence",
    "AI model confidence for risk prediction",
    ["entity_id", "prediction_type"],
    registry=risk_registry
)

# Model accuracy metrics
model_accuracy = Gauge(
    "risk_model_accuracy",
    "Risk model accuracy metrics",
    ["metric_type"],  # precision, recall, f1, auc
    registry=risk_registry
)


# ============================================
# DATA MODELS
# ============================================

class ContributingFactor(BaseModel):
    name: str
    weight: float  # 0-100
    description: str
    anomaly_count: int
    severity: str  # critical, high, medium, low


class EntityRiskProfile(BaseModel):
    entity_id: str
    entity_name: str
    entity_type: str
    risk_score: float
    confidence: float
    contributing_factors: List[ContributingFactor]
    risk_level: str
    last_updated: str


class RiskSummary(BaseModel):
    total_entities: int
    avg_risk_score: float
    distribution: Dict[str, int]
    top_risk_entities: List[Dict[str, Any]]
    recent_alerts: List[Dict[str, Any]]


# ============================================
# MOCK DATA (To be replaced with real AI/ML engine)
# ============================================

# Sample entities data
SAMPLE_ENTITIES = {
    "VENDOR-001": {
        "name": "PT. Maju Jaya",
        "type": "vendor",
        "base_risk": 85,
        "factors": [
            {"name": "Circular payment pattern", "weight": 35, "severity": "critical"},
            {"name": "Vendor concentration", "weight": 25, "severity": "high"},
            {"name": "Timing anomaly", "weight": 20, "severity": "medium"},
            {"name": "Graph centrality", "weight": 12, "severity": "medium"},
            {"name": "Historical fraud similarity", "weight": 8, "severity": "low"}
        ]
    },
    "VENDOR-002": {
        "name": "CV. Karya Mandiri",
        "type": "vendor",
        "base_risk": 92,
        "factors": [
            {"name": "Single bidder pattern", "weight": 40, "severity": "critical"},
            {"name": "Unusual spending spike", "weight": 30, "severity": "high"},
            {"name": "Address collusion", "weight": 18, "severity": "high"},
            {"name": "Conflict of interest", "weight": 12, "severity": "medium"}
        ]
    },
    "INST-001": {
        "name": "Kementerian PUPR",
        "type": "institution",
        "base_risk": 45,
        "factors": [
            {"name": "Lack of competitive bidding", "weight": 25, "severity": "medium"},
            {"name": "Budget deviation", "weight": 15, "severity": "low"},
            {"name": "Delayed reporting", "weight": 5, "severity": "low"}
        ]
    },
    "VENDOR-003": {
        "name": "PT. Bangun Nusantara",
        "type": "vendor",
        "base_risk": 78,
        "factors": [
            {"name": "Bid rigging pattern", "weight": 35, "severity": "critical"},
            {"name": "Subcontractor loop", "weight": 25, "severity": "high"},
            {"name": "Shell company indicators", "weight": 18, "severity": "high"},
            {"name": "Abnormal pricing", "weight": 12, "severity": "medium"}
        ]
    },
    "INDIV-001": {
        "name": "Dr. Ahmad Fauzi",
        "type": "individual",
        "base_risk": 68,
        "factors": [
            {"name": "Nepotism pattern", "weight": 30, "severity": "high"},
            {"name": "Undisclosed relationship", "weight": 25, "severity": "high"},
            {"name": "Influence peddling", "weight": 20, "severity": "medium"},
            {"name": "Asset discrepancy", "weight": 15, "severity": "medium"}
        ]
    }
}


def get_entity_risk_profile(entity_id: str) -> Optional[EntityRiskProfile]:
    """Get risk profile for a specific entity"""
    if entity_id not in SAMPLE_ENTITIES:
        return None
    
    data = SAMPLE_ENTITIES[entity_id]
    factors = []
    
    for f in data["factors"]:
        factors.append(ContributingFactor(
            name=f["name"],
            weight=f["weight"],
            description=f"Detected {f['name'].lower()} indicating potential fraud",
            anomaly_count=random.randint(1, 15),
            severity=f["severity"]
        ))
    
    # Determine risk level based on score
    risk_score = data["base_risk"]
    if risk_score >= 85:
        risk_level = "critical"
    elif risk_score >= 70:
        risk_level = "high"
    elif risk_score >= 40:
        risk_level = "medium"
    else:
        risk_level = "low"
    
    return EntityRiskProfile(
        entity_id=entity_id,
        entity_name=data["name"],
        entity_type=data["type"],
        risk_score=risk_score,
        confidence=random.uniform(85, 98),
        contributing_factors=factors,
        risk_level=risk_level,
        last_updated=datetime.now().isoformat()
    )


async def update_risk_metrics():
    """Update Prometheus metrics for risk dashboard"""
    # Update risk distribution
    risk_levels = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    
    for entity_id, data in SAMPLE_ENTITIES.items():
        score = data["base_risk"]
        entity_risk_score.labels(
            entity_id=entity_id,
            entity_name=data["name"],
            entity_type=data["type"]
        ).set(score)
        
        if score >= 85:
            risk_levels["critical"] += 1
        elif score >= 70:
            risk_levels["high"] += 1
        elif score >= 40:
            risk_levels["medium"] += 1
        else:
            risk_levels["low"] += 1
        
        # Update contributing factors metrics
        for factor in data["factors"]:
            risk_contributing_factor.labels(
                entity_id=entity_id,
                factor_name=factor["name"]
            ).set(factor["weight"])
    
    # Set distribution metrics
    for level, count in risk_levels.items():
        risk_distribution.labels(risk_level=level).set(count)
    
    # Calculate and set average risk score
    total_score = sum(d["base_risk"] for d in SAMPLE_ENTITIES.values())
    avg_score = total_score / len(SAMPLE_ENTITIES)
    avg_risk_score.set(avg_score)
    
    # Set model accuracy metrics (mock data)
    model_accuracy.labels(metric_type="precision").set(0.92)
    model_accuracy.labels(metric_type="recall").set(0.88)
    model_accuracy.labels(metric_type="f1").set(0.90)
    model_accuracy.labels(metric_type="auc").set(0.94)


@router.get("/")
async def get_risk_metrics():
    """Endpoint for risk metrics"""
    await update_risk_metrics()
    return Response(
        content=generate_latest(risk_registry),
        media_type=CONTENT_TYPE_LATEST
    )


@router.get("/entity/{entity_id}")
async def get_entity_risk(entity_id: str) -> EntityRiskProfile:
    """Get detailed risk profile for an entity"""
    profile = get_entity_risk_profile(entity_id)
    if not profile:
        return Response(status_code=404, content={"error": "Entity not found"})
    return profile


@router.get("/summary")
async def risk_summary() -> RiskSummary:
    """Get overall risk summary"""
    await update_risk_metrics()
    
    entities = []
    risk_levels = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    
    for entity_id, data in SAMPLE_ENTITIES.items():
        score = data["base_risk"]
        if score >= 85:
            risk_level = "critical"
            risk_levels["critical"] += 1
        elif score >= 70:
            risk_level = "high"
            risk_levels["high"] += 1
        elif score >= 40:
            risk_level = "medium"
            risk_levels["medium"] += 1
        else:
            risk_level = "low"
            risk_levels["low"] += 1
        
        entities.append({
            "entity_id": entity_id,
            "entity_name": data["name"],
            "entity_type": data["type"],
            "risk_score": score,
            "risk_level": risk_level
        })
    
    # Sort by risk score descending and get top 5
    top_entities = sorted(entities, key=lambda x: x["risk_score"], reverse=True)[:5]
    
    # Mock recent alerts
    recent_alerts = [
        {"time": "10:32:15", "entity": "VENDOR-002", "risk_score": 92, "message": "Single bidder pattern detected"},
        {"time": "10:28:00", "entity": "VENDOR-001", "risk_score": 85, "message": "Circular payment pattern detected"},
        {"time": "10:15:30", "entity": "PT. Bangun Nusantara", "risk_score": 78, "message": "Bid rigging pattern detected"},
        {"time": "09:45:12", "entity": "VENDOR-003", "risk_score": 78, "message": "Subcontractor loop detected"}
    ]
    
    return RiskSummary(
        total_entities=len(SAMPLE_ENTITIES),
        avg_risk_score=sum(d["base_risk"] for d in SAMPLE_ENTITIES.values()) / len(SAMPLE_ENTITIES),
        distribution=risk_levels,
        top_risk_entities=top_entities,
        recent_alerts=recent_alerts
    )


@router.get("/explain/{entity_id}")
async def explain_risk(entity_id: str):
    """Get explainable risk breakdown for an entity"""
    profile = get_entity_risk_profile(entity_id)
    if not profile:
        return Response(status_code=404, content={"error": "Entity not found"})
    
    explanation = {
        "entity_id": profile.entity_id,
        "entity_name": profile.entity_name,
        "overall_risk_score": profile.risk_score,
        "confidence": profile.confidence,
        "risk_level": profile.risk_level,
        "explanation": f"Entity '{profile.entity_name}' has a {profile.risk_level.upper()} risk score of {profile.risk_score} based on {len(profile.contributing_factors)} contributing factors.",
        "contributing_factors": [
            {
                "factor": f.name,
                "weight": f.weight,
                "impact": f"Weight {f.weight}% toward overall risk score",
                "severity": f.severity,
                "recommendation": _get_recommendation(f.name)
            }
            for f in profile.contributing_factors
        ],
        "risk_breakdown": {
            "anomaly_score": profile.risk_score * 0.4,
            "graph_centrality": profile.risk_score * 0.25,
            "historical_pattern": profile.risk_score * 0.2,
            "compliance_deviation": profile.risk_score * 0.15
        },
        "mitigation_steps": [
            "Review all transactions with this entity",
            "Verify beneficial ownership documentation",
            "Conduct enhanced due diligence",
            "Monitor for 6 months with increased frequency"
        ],
        "last_updated": profile.last_updated
    }
    
    return explanation


def _get_recommendation(factor_name: str) -> str:
    """Get recommendation based on factor type"""
    recommendations = {
        "Circular payment pattern": "Conduct forensic audit of payment flows",
        "Single bidder pattern": "Require competitive bidding for future contracts",
        "Unusual spending spike": "Review procurement justifications",
        "Address collusion": "Verify legal entity separation",
        "Conflict of interest": "Disclose all related party transactions",
        "Bid rigging pattern": "Investigate bidding process integrity",
        "Subcontractor loop": "Map complete subcontractor network",
        "Shell company indicators": "Request audited financial statements"
    }
    return recommendations.get(factor_name, "Initiate enhanced monitoring")


@router.get("/trend/{entity_id}")
async def risk_trend(entity_id: str, days: int = 30):
    """Get risk score trend for an entity"""
    if entity_id not in SAMPLE_ENTITIES:
        return Response(status_code=404, content={"error": "Entity not found"})
    
    # Generate mock trend data
    base_score = SAMPLE_ENTITIES[entity_id]["base_risk"]
    trend = []
    
    for i in range(days):
        # Add some variance to make trend realistic
        variance = random.uniform(-5, 8)
        score = min(100, max(0, base_score + variance - (i * 0.1)))
        trend.append({
            "date": (datetime.now().timestamp() - (days - i) * 86400) * 1000,
            "risk_score": round(score, 1)
        })
    
    return {
        "entity_id": entity_id,
        "entity_name": SAMPLE_ENTITIES[entity_id]["name"],
        "trend": trend,
        "trend_direction": "increasing" if trend[-1]["risk_score"] > trend[0]["risk_score"] else "decreasing",
        "change_percentage": round(((trend[-1]["risk_score"] - trend[0]["risk_score"]) / trend[0]["risk_score"]) * 100, 1)
    }
