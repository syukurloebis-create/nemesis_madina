from typing import Dict, List


class CourtReadiness:
    """
    Menilai kesiapan bukti untuk pengadilan
    """

    def evaluate(self, chain: List[Dict], integrity_ok: bool) -> Dict:

        score = 0

        # jumlah evidence
        if len(chain) > 10:
            score += 0.3
        elif len(chain) > 3:
            score += 0.2
        else:
            score += 0.1

        # integrity
        if integrity_ok:
            score += 0.5

        # continuity
        timestamps = [c.get("timestamp") for c in chain]
        if len(timestamps) > 1:
            score += 0.2

        return {
            "court_readiness_score": round(min(score, 1.0), 4),
            "status": "READY" if score > 0.7 else "NOT_READY"
        }