# backend/ml/scoring/confidence.py
import math
from typing import Dict, Any

class ConfidenceScorer:
    """Hitung confidence score berdasarkan data quality."""
    
    @staticmethod
    def compute(
        event_count: int,
        data_completeness: float = 1.0,
        chain_integrity: bool = True
    ) -> float:
        if event_count == 0:
            count_factor = 0.1
        elif event_count == 1:
            count_factor = 0.5
        else:
            count_factor = min(0.95, 0.6 + math.log(event_count) / 20)
        
        integrity_factor = 1.0 if chain_integrity else 0.3
        confidence = (count_factor * 0.5) + (data_completeness * 0.3) + (integrity_factor * 0.2)
        confidence = min(0.95, max(0.3, round(confidence, 4)))
        return confidence
    
    @staticmethod
    def data_completeness(payload: Dict) -> float:
        required_fields = ['pagu', 'opd', 'metode']
        optional_fields = ['nama_paket', 'bulan', 'lokasi']
        
        required_present = sum(1 for f in required_fields if f in payload)
        optional_present = sum(1 for f in optional_fields if f in payload)
        
        required_score = required_present / len(required_fields)
        optional_score = optional_present / len(optional_fields)
        
        return (required_score * 0.7) + (optional_score * 0.3)
