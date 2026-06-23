# backend/ml/scoring/soft_scoring.py
"""
Soft Scoring Engine untuk NEMESIS V8+
Mengganti hard-threshold dengan continuous scoring (0-1)
"""
import math
from typing import Dict, Any, Tuple, List


def normalize_pagu(pagu: float, max_pagu: float = 2_000_000_000) -> float:
    """
    Normalisasi pagu menggunakan log scale.
    - Bukan binary high/low
    - Smooth transition 0-1
    """
    if not pagu or pagu <= 0:
        return 0.0
    log_value = math.log1p(pagu)
    log_max = math.log1p(max_pagu)
    score = min(1.0, log_value / log_max)
    return round(score, 4)


def soft_anomaly_score(pagu: float, threshold: float = 500_000_000) -> float:
    """
    Anomaly score menggunakan tanh (sigmoid-like).
    - Smooth transition
    - Tidak ekstrem
    """
    if not pagu or pagu <= 0:
        return 0.0
    ratio = pagu / threshold
    score = math.tanh(ratio - 0.5)
    score = max(0.0, min(1.0, (score + 1) / 2))
    return round(score, 4)


def duplicate_penalty(duplicate_count: int, max_penalty: float = 0.3) -> float:
    """
    Penalty untuk duplicate event.
    - Tidak langsung 0.2 per duplicate
    - Diminishing returns
    """
    if duplicate_count <= 1:
        return 0.0
    penalty = max_penalty * (1 - math.exp(-duplicate_count / 5))
    return round(penalty, 4)


def suspicious_method_penalty(metode: str, pagu: float) -> float:
    """
    Penalty untuk metode pengadaan yang mencurigakan.
    """
    if metode in ["Pengadaan Langsung", "Direct Procurement"]:
        if pagu > 1_000_000_000:
            return 0.25
        elif pagu > 500_000_000:
            return 0.15
        elif pagu > 100_000_000:
            return 0.08
    return 0.0


def compute_risk_score(
    anomaly_score: float,
    business_score: float,
    chain_integrity: bool,
    weights: Dict[str, float] = None
) -> float:
    """
    Risk score dengan weighted soft model.
    Default weights: anomaly 45%, business 35%, chain 20%
    """
    if weights is None:
        weights = {
            "anomaly": 0.45,
            "business": 0.35,
            "chain": 0.20
        }
    
    chain_factor = 0.0 if chain_integrity else 1.0
    
    risk = (
        weights["anomaly"] * anomaly_score +
        weights["business"] * (1 - business_score) +
        weights["chain"] * chain_factor
    )
    
    # Dampening agar tidak ekstrem
    risk = risk / (1 + abs(risk - 0.5) * 0.5)
    risk = min(0.95, max(0.05, round(risk, 4)))
    
    return risk


def compute_trust_score(
    chain_integrity: bool,
    business_score: float,
    risk_score: float,
    weights: Dict[str, float] = None
) -> float:
    """
    Trust score dengan balanced model.
    Jangan hanya inverse risk.
    """
    if weights is None:
        weights = {
            "chain": 0.35,
            "business": 0.35,
            "risk_inverse": 0.30
        }
    
    chain_factor = 1.0 if chain_integrity else 0.0
    risk_inverse = 1.0 - risk_score
    
    trust = (
        weights["chain"] * chain_factor +
        weights["business"] * business_score +
        weights["risk_inverse"] * risk_inverse
    )
    
    # Dampening
    trust = trust / (1 + abs(trust - 0.5) * 0.3)
    trust = min(0.95, max(0.05, round(trust, 4)))
    
    return trust


def get_level(score: float) -> str:
    """Konversi score ke level."""
    if score >= 0.7:
        return "HIGH"
    elif score >= 0.4:
        return "MEDIUM"
    else:
        return "LOW"


def compute_all_scores(
    pagu: float,
    duplicate_count: int,
    event_count: int,
    metode: str,
    chain_integrity: bool
) -> Tuple[float, float, float, List[Dict]]:
    """
    Hitung semua score sekaligus.
    Returns: (risk_score, trust_score, business_score, anomaly_factors)
    """
    # Normalisasi pagu ke business score
    business_score = normalize_pagu(pagu)
    
    # Soft anomaly scoring
    anomaly_base = soft_anomaly_score(pagu)
    duplicate_pen = duplicate_penalty(duplicate_count)
    method_pen = suspicious_method_penalty(metode, pagu)
    
    anomaly_score = min(1.0, anomaly_base + duplicate_pen + method_pen)
    anomaly_score = round(anomaly_score, 4)
    
    # Build anomaly factors untuk response
    anomaly_factors = []
    if anomaly_base > 0.1:
        anomaly_factors.append({
            "type": "high_value_procurement",
            "weight": anomaly_base,
            "value": pagu
        })
    if duplicate_pen > 0:
        anomaly_factors.append({
            "type": "duplicate_pattern",
            "weight": duplicate_pen,
            "count": duplicate_count
        })
    if method_pen > 0:
        anomaly_factors.append({
            "type": "suspicious_method",
            "weight": method_pen,
            "method": metode
        })
    
    # Risk dan Trust
    risk_score = compute_risk_score(anomaly_score, business_score, chain_integrity)
    trust_score = compute_trust_score(chain_integrity, business_score, risk_score)
    
    return risk_score, trust_score, business_score, anomaly_factors

def compute_confidence_score(
    event_count: int,
    chain_integrity: bool,
    payload: Dict = None
) -> float:
    """Hitung confidence score untuk response."""
    from ml.scoring.confidence import ConfidenceScorer
    
    data_completeness = 1.0
    if payload:
        data_completeness = ConfidenceScorer.data_completeness(payload)
    
    return ConfidenceScorer.compute(event_count, data_completeness, chain_integrity)
