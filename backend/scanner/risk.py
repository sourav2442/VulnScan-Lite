def calculate_risk(score):

    if score >= 90:
        return "Low"

    elif score >= 70:
        return "Medium"

    elif score >= 50:
        return "High"

    return "Critical"