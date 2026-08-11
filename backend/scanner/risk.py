def calculate_risk(score):
    """
    Calculate risk level from the overall security score.
    """

    score = max(0, min(int(score), 100))

    if score >= 90:
        return "Low"

    elif score >= 70:
        return "Medium"

    elif score >= 50:
        return "High"

    return "Critical"