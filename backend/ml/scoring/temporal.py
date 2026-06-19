# backend/ml/scoring/temporal.py
from datetime import datetime, timezone
from typing import Optional

class TemporalDecay:
    """Temporal decay untuk risk dan trust."""
    
    @staticmethod
    def decay_factor(last_activity: datetime, half_life_days: float = 90) -> float:
        """Hitung decay factor berdasarkan waktu sejak aktivitas terakhir."""
        now = datetime.now(timezone.utc)
        days_passed = (now - last_activity).days
        
        if days_passed <= 0:
            return 1.0
        
        # Exponential decay: factor = 0.5^(days_passed / half_life)
        factor = 0.5 ** (days_passed / half_life_days)
        return max(0.1, min(1.0, factor))
    
    @staticmethod
    def apply_decay(score: float, days_passed: int, half_life: float = 90) -> float:
        """Terapkan decay ke score."""
        factor = 0.5 ** (days_passed / half_life)
        decayed = score * factor
        return max(0.05, min(0.95, round(decayed, 4)))