import statistics
from typing import Dict, List


class AnomalyEngine:

    def detect(
        self,
        events: List[Dict]
    ) -> Dict:

        pagu_values = []

        for event in events:

            payload = event.get(
                "payload",
                {}
            )

            pagu = payload.get("pagu")

            if isinstance(
                pagu,
                (int, float)
            ):
                pagu_values.append(
                    float(pagu)
                )

        if len(pagu_values) < 2:
            return {
                "anomaly_score": 0.0,
                "outliers": []
            }

        mean = statistics.mean(
            pagu_values
        )

        std = statistics.stdev(
            pagu_values
        )

        outliers = []

        for value in pagu_values:

            if std > 0:

                z_score = abs(
                    (value - mean)
                    / std
                )

                if z_score > 2:
                    outliers.append(
                        value
                    )

        anomaly_score = min(
            len(outliers) * 2,
            10
        )

        return {
            "anomaly_score": anomaly_score,
            "outliers": outliers
        }