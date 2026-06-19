# backend/ml/anomaly/classifier.py
from enum import Enum
from typing import Dict, Any, List

class AnomalyType(Enum):
    STRUCTURAL = "structural"      # Duplicate event, missing sequence
    FINANCIAL = "financial"        # High value, suspicious threshold
    BEHAVIORAL = "behavioral"      # Pattern anomaly, velocity


class AnomalyClassifier:
    """Klasifikasi anomaly berdasarkan jenis."""
    
    @staticmethod
    def classify(pagu: float, duplicate_count: int, metode: str) -> List[Dict]:
        """Klasifikasi anomaly ke dalam jenis."""
        anomalies = []
        
        # Financial anomaly
        if pagu > 1_000_000_000:
            anomalies.append({
                "type": AnomalyType.FINANCIAL.value,
                "severity": min(0.8, 0.5 + (pagu - 1_000_000_000) / 10_000_000_000),
                "description": f"High value procurement: {pagu:,.0f}"
            })
        
        # Structural anomaly
        if duplicate_count > 1:
            anomalies.append({
                "type": AnomalyType.STRUCTURAL.value,
                "severity": min(0.6, duplicate_count * 0.15),
                "description": f"Duplicate events detected: {duplicate_count}"
            })
        
        # Behavioral anomaly
        if metode in ["Pengadaan Langsung", "Direct Procurement"]:
            anomalies.append({
                "type": AnomalyType.BEHAVIORAL.value,
                "severity": 0.4 if pagu > 500_000_000 else 0.2,
                "description": f"Suspicious method: {metode}"
            })
        
        return anomalies