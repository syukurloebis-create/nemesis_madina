def confidence_from_score(
    trust: float
):

    if trust >= 85:
        return "HIGH"

    if trust >= 70:
        return "MEDIUM"

    if trust >= 50:
        return "LOW"

    return "VERY_LOW"