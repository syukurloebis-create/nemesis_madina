def calculate_confidence(score: float) -> str:

    if score >= 90:
        return "HIGH"

    if score >= 70:
        return "MEDIUM"

    if score >= 40:
        return "LOW"

    return "VERY_LOW"