"""
Risk Model – Stable risk scoring engine (V8+)
Mengganti heuristic inline dengan deterministic computation
"""

import math
from typing import Dict, Optional


class RiskModel:
    """
    Stable risk scoring dengan log-scale dan volatility damping
    Range output: 0.0 (low risk) – 1.0 (high risk)
    """

    def __init__(self):
        self.alpha = 0.7  # Smoothing factor for anomaly
        self.max_anomaly_contribution = 0.34


    def compute(
        self,
        features: Dict[str, float],
        anomaly_score: float = 0.0,
        previous_risk: Optional[float] = None
    ) -> float:
        """
        Compute deterministic risk score

        Args:
            features: Output dari FeatureEngine.extract()
            anomaly_score: Raw anomaly score (0-10 scale)
            previous_risk: Previous risk score untuk smoothing opsional

        Returns:
            Risk score antara 0.0 – 1.0
        """
        # 1. Normalize anomaly (cap agar tidak dominan)
        normalized_anomaly = self._normalize_anomaly(anomaly_score)
        capped_anomaly = min(normalized_anomaly, self.max_anomaly_contribution)

        # 2. PAGU risk dengan log-scale (stabilizer kritis)
        avg_pagu = max(
            0.0,
            float(features.get("avg_pagu", 0))
        )

        pagu_score = self._compute_pagu_risk(avg_pagu)

        # 3. Volatility risk dari standard deviation
        volatility = self._compute_volatility_risk(features)

        # 4. Structural risk (event count & diversity)
        structural_risk = self._compute_structural_risk(features)

        # 5. Business size risk (jika pagu besar)
        size_risk = self._compute_size_risk(features)

        # FINAL WEIGHTED SCORE (STABILIZED)
        baseline_risk = 0.20

        raw_risk = (
            baseline_risk +
            0.18 * pagu_score +
            0.15 * volatility +
            0.15 * structural_risk +
            0.15 * size_risk +
            capped_anomaly
        )

        # Clamp 0..1
        final_risk = max(0.0, min(raw_risk, 0.70))

        # Optional smoothing
        if previous_risk is not None:
            final_risk = (
                0.7 * previous_risk +
                0.3 * final_risk
            )

        return round(final_risk, 4)


    def _normalize_anomaly(self, raw_anomaly: float) -> float:
        """
        Normalisasi anomaly score ke range [0, 1]
        Dengan diminishing returns untuk nilai ekstrem
        """
        if raw_anomaly <= 0:
            return 0.0

        # Anomaly biasanya 0-10, map ke 0-0.5 maximum
        # sehingga tidak bisa sendirian membuat risk tinggi
        normalized = raw_anomaly / 20.0  # 10 → 0.5, 5 → 0.25
        return min(normalized, 0.5)


    def _compute_pagu_risk(self, avg_pagu: float) -> float:
        """
        Log-scale pagu risk
        Risk meningkat secara log, bukan linear
        """
        if avg_pagu <= 0:
            return 0.0

        # Log10 scale: 1jt → 0.33, 10M → 0.44, 100M → 0.55, 1M → 0.66
        # Range: 0.0 - 0.8 (tidak pernah 1.0)
        log_pagu = math.log10(avg_pagu + 1) / 7
        return min(log_pagu, 0.8)


    def _compute_volatility_risk(self, features: Dict[str, float]) -> float:
        """
        Volatility risk dari coefficient of variation
        CV tinggi = risk tinggi
        """
        coef_var = features.get("pagu_coef_var", 0.0)

        # CV > 1 menunjukkan variasi ekstrem
        if coef_var > 1.0:
            return 0.7
        elif coef_var > 0.5:
            return 0.4
        elif coef_var > 0.2:
            return 0.2
        else:
            return 0.05


    def _compute_structural_risk(self, features: Dict[str, float]) -> float:
        """
        Structural risk berdasarkan event count
        Semakin banyak event, semakin stabil (risk turun)
        """
        event_count = features.get("event_count", 0.0)

        if event_count == 0:
            return 0.3  # No data = moderate risk
        elif event_count == 1:
            return 0.25  # Single event = slightly elevated
        elif event_count <= 3:
            return 0.15
        elif event_count <= 10:
            return 0.05
        else:
            return 0.05  # Many events = stable


    def _compute_size_risk(self, features: Dict[str, float]) -> float:
        has_large_pagu = features.get("has_large_pagu", 0)

        if has_large_pagu > 0:
            return 0.65  # Large transaction = elevated scrutiny
        return 0.0