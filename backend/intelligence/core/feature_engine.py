"""
Feature Engine – Extract stable features from event lineage
Tidak merusak sistem existing, hanya ekstraksi data
"""

import statistics
from typing import List, Dict, Any


class FeatureEngine:
    """
    Extract deterministic features from event list
    Semua nilai selalu dalam range yang stabil
    """

    def extract(self, events: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Extract features dari event lineage

        Args:
            events: List of event dictionaries

        Returns:
            Dictionary dengan feature keys
        """
        if not events:
            return self._empty_features()

        # Extract pagu values from payload
        pagu_values = []
        for event in events:
            payload = event.get("payload", {})
            if isinstance(payload, dict):
                pagu = payload.get("pagu", 0)
                if isinstance(pagu, (int, float)) and pagu > 0:
                    pagu_values.append(float(pagu))

        # Calculate statistics
        if pagu_values:
            avg_pagu = statistics.mean(pagu_values)
            max_pagu = max(pagu_values)
            min_pagu = min(pagu_values)
            pagu_std = statistics.pstdev(pagu_values) if len(pagu_values) > 1 else 0.0
        else:
            avg_pagu = max_pagu = min_pagu = pagu_std = 0.0

        # Additional stability metrics
        total_events = len(events)

        return {
            "event_count": float(total_events),
            "avg_pagu": round(avg_pagu, 2),
            "max_pagu": round(max_pagu, 2),
            "min_pagu": round(min_pagu, 2),
            "pagu_std": round(pagu_std, 2),
            "pagu_coef_var": round(pagu_std / (avg_pagu + 0.01), 4),  # volatility proxy
            "has_multiple_events": 1.0 if total_events > 1 else 0.0,
            "has_large_pagu": 1.0 if max_pagu > 1_000_000_000 else 0.0,  # > 1M
        }

    def _empty_features(self) -> Dict[str, float]:
        """Return empty/zero features untuk entity tanpa events"""
        return {
            "event_count": 0.0,
            "avg_pagu": 0.0,
            "max_pagu": 0.0,
            "min_pagu": 0.0,
            "pagu_std": 0.0,
            "pagu_coef_var": 0.0,
            "has_multiple_events": 0.0,
            "has_large_pagu": 0.0,
        }