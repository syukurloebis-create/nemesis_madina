# backend/ml/scoring/calibration.py
import statistics
import math
from typing import Dict, Any

class RiskCalibrator:
    """Global risk calibration menggunakan z-score."""
    
    _global_stats = None
    
    @classmethod
    def get_global_stats(cls, pool=None):
        """Hitung mean dan std dev global."""
        if cls._global_stats:
            return cls._global_stats
        
        # Hitung dari database (caching)
        import asyncpg
        import os
        
        async def _fetch():
            dsn = os.getenv("PG_DSN", "postgresql://nemesis:nemesis123@localhost:5432/madina")
            conn = await asyncpg.connect(dsn)
            rows = await conn.fetch("""
                SELECT CAST(payload->>'pagu' AS FLOAT) as pagu
                FROM event_lineage
                WHERE payload->>'pagu' IS NOT NULL
            """)
            await conn.close()
            
            pagus = [r['pagu'] for r in rows if r['pagu'] and r['pagu'] > 0]
            if not pagus:
                return {"mean": 500_000_000, "std": 300_000_000}
            
            return {
                "mean": statistics.mean(pagus),
                "std": statistics.stdev(pagus) if len(pagus) > 1 else 300_000_000
            }
        
        import asyncio
        cls._global_stats = asyncio.run(_fetch())
        return cls._global_stats
    
    @classmethod
    def calibrate_risk(cls, raw_risk: float, pagu: float) -> float:
        """Kalibrasi risk berdasarkan posisi relatif terhadap populasi."""
        stats = cls.get_global_stats()
        if pagu <= 0:
            return raw_risk
        
        z_score = (pagu - stats["mean"]) / stats["std"]
        # Konversi z-score ke faktor kalibrasi (0.7 - 1.3)
        calibration_factor = 1.0 + (z_score / 10)
        calibration_factor = max(0.7, min(1.3, calibration_factor))
        
        calibrated = raw_risk * calibration_factor
        return round(min(0.95, max(0.05, calibrated)), 4)