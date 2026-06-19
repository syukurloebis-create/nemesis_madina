"""
Confidence Model V8+
Mengukur kualitas data & stabilitas sinyal
"""

from typing import Dict


class ConfidenceModel:

    def compute(self, features: Dict) -> float:

        event_count = features.get("event_count", 0)
        pagu_var = features.get("pagu_coef_var", 1.0)
        has_data = 1 if event_count > 0 else 0

        # base confidence
        base = 0.3

        # more data = more confidence
        data_factor = min(event_count / 20, 0.4)

        # stability = low variance → high confidence
        stability = max(0.0, 0.3 - pagu_var)

        score = base + data_factor + stability + (0.1 * has_data)

        return round(max(0.0, min(score, 1.0)), 4)