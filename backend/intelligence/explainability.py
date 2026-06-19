class ExplainabilityEngine:
    def generate_reasons(self, score: float, factors: dict) -> list:
        reasons = []
        for factor, value in factors.items():
            if value.get('impact') == 'high':
                reasons.append({
                    "factor": factor,
                    "description": f"{factor} memiliki dampak tinggi terhadap skor",
                    "value": value.get('value')
                })
        return reasons
