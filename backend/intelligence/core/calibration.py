"""
Calibration Layer – Stateful smoothing & normalization
Mencegah extreme spikes dan menjaga kestabilan score
"""

from datetime import datetime, UTC
from typing import Dict, Optional
from datetime import datetime, timedelta


class Calibration:
    """
    Stateful calibration per entity
    Menyimpan history score untuk temporal smoothing
    """

    def __init__(self, max_history_minutes: int = 60):
        self._risk_history: Dict[str, Dict] = {}  # entity_id -> {score, timestamp}
        self._trust_history: Dict[str, Dict] = {}
        self.max_age = timedelta(minutes=max_history_minutes)

    def smooth_risk(
        self,
        entity_id: str,
        current_risk: float,
        alpha: float = 0.70
    ) -> float:
        """
        Smooth risk score dengan previous value

        Args:
            entity_id: Entity identifier
            current_risk: Current risk score (0-1)
            alpha: Weight for previous value (higher = more stable)

        Returns:
            Smoothed risk score
        """
        previous = self._get_previous_risk(entity_id)

        if previous is None:
            # First time for this entity
            self._risk_history[entity_id] = {
                "score": current_risk,
                "timestamp": datetime.now(UTC)
            }
            return round(current_risk, 4)

        # Exponential smoothing
        smoothed = (alpha * previous["score"]) + ((1 - alpha) * current_risk)
        final_risk = round(smoothed, 4)

        # Update history
        self._risk_history[entity_id] = {
            "score": final_risk,
            "timestamp": datetime.now(UTC)
        }

        return final_risk

    def smooth_trust(
        self,
        entity_id: str,
        current_trust: float,
        alpha: float = 0.85
    ) -> float:
        """
        Smooth trust score (lebih stabil dari risk)
        """
        previous = self._get_previous_trust(entity_id)

        if previous is None:
            self._trust_history[entity_id] = {
                "score": current_trust,
                "timestamp": datetime.now(UTC)
            }
            return round(current_trust, 4)

        # Trust lebih stabil → alpha lebih tinggi
        smoothed = (alpha * previous["score"]) + ((1 - alpha) * current_trust)
        final_trust = round(smoothed, 4)

        self._trust_history[entity_id] = {
            "score": final_trust,
            "timestamp": datetime.now(UTC)
        }

        return final_trust

    def normalize_score(self, raw_score: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
        """
        Clamp score ke range yang diinginkan
        """
        return max(min_val, min(raw_score, max_val))

    def dampen_extreme(self, score: float, threshold: float = 0.85) -> float:
        """
        Dampen extreme scores (> threshold)
        Mencegah panic scoring
        """
        if score > threshold:
            # Reduce extreme score: 0.95 → 0.85
            overshoot = score - threshold
            dampened = threshold + (overshoot * 0.3)
            return round(dampened, 4)
        return score

    def _get_previous_risk(self, entity_id: str) -> Optional[Dict]:
        """Get previous risk score if not expired"""
        if entity_id not in self._risk_history:
            return None

        record = self._risk_history[entity_id]
        age = datetime.now(UTC) - record["timestamp"]

        if age > self.max_age:
            # Expired, remove and return None
            del self._risk_history[entity_id]
            return None

        return record

    def _get_previous_trust(self, entity_id: str) -> Optional[Dict]:
        """Get previous trust score if not expired"""
        if entity_id not in self._trust_history:
            return None

        record = self._trust_history[entity_id]
        age = datetime.now(UTC) - record["timestamp"]

        if age > self.max_age:
            del self._trust_history[entity_id]
            return None

        return record

    def clear_history(self, entity_id: Optional[str] = None):
        """
        Clear history untuk entity tertentu atau semua
        """
        if entity_id:
            self._risk_history.pop(entity_id, None)
            self._trust_history.pop(entity_id, None)
        else:
            self._risk_history.clear()
            self._trust_history.clear()