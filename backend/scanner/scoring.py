def calculate_score(passed, total):
    """
    Calculate the security header score and grade.
    """

    if total <= 0:
        return 0, "F"

    score = round((passed / total) * 100)

    if score >= 90:
        grade = "A+"
    elif score >= 80:
        grade = "A"
    elif score >= 70:
        grade = "B"
    elif score >= 60:
        grade = "C"
    elif score >= 50:
        grade = "D"
    else:
        grade = "F"

    return score, grade