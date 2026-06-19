import hashlib
from typing import Dict, Any, List


class CollusionService:
    def __init__(self, repository):
        self.repository = repository

    def _generate_pattern_key(self, pattern: Dict[str, Any]) -> str:
        """
        Create deterministic fingerprint for deduplication
        """
        raw = {
            "type": pattern.get("type"),
            "entities": sorted(pattern.get("entities", [])),
            "cycle": pattern.get("cycle"),
        }

        encoded = str(raw).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def analyze(self, case_id: str, graph: Dict[str, Any]) -> Dict:
        patterns = self._detect_patterns(graph)

        saved_patterns = []

        for p in patterns:
            pattern_key = self._generate_pattern_key(p)
            p["pattern_key"] = pattern_key

            existing = self.repository.get_by_pattern_key(case_id, pattern_key)

            if existing:
                saved_patterns.append(existing)
                continue

            saved = self.repository.save(case_id, p)
            saved_patterns.append(saved)

        return {
            "case_id": case_id,
            "triangles_found": len(patterns),
            "collusion_risk": self._calculate_risk(patterns),
            "detected_patterns": saved_patterns,
            "saved_detections": len(saved_patterns),
        }

    def _detect_patterns(self, graph: Dict[str, Any]) -> List[Dict]:
        # placeholder existing logic
        return graph.get("detected_patterns", [])

    def _calculate_risk(self, patterns: List[Dict]) -> float:
        if not patterns:
            return 0.0

        return min(100.0, sum(p.get("severity", 0.5) * 50 for p in patterns))