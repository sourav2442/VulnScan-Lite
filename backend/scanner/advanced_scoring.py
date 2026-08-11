def calculate_overall_score(header_result, ssl_result, cms_result):
    """
    Calculate the overall security score.

    Weighting:
        Security Headers = 50 points
        SSL/TLS          = 30 points
        CMS              = 20 points
    """

    score = 0

    # -------------------------
    # Header Score: 50 points
    # -------------------------

    passed_headers = len(
        header_result.get("passed_checks", [])
    )

    failed_headers = len(
        header_result.get("failed_checks", [])
    )

    total_headers = passed_headers + failed_headers

    if total_headers > 0:
        header_score = round(
            (passed_headers / total_headers) * 50
        )
        score += header_score

    # -------------------------
    # SSL Score: 30 points
    # -------------------------

    if (
        ssl_result.get("enabled")
        and ssl_result.get("valid")
    ):
        days_remaining = ssl_result.get(
            "days_remaining"
        )

        if days_remaining is None:
            score += 15

        elif days_remaining > 90:
            score += 30

        elif days_remaining > 30:
            score += 25

        elif days_remaining > 7:
            score += 15

        elif days_remaining > 0:
            score += 5

    # -------------------------
    # CMS Score: 20 points
    # -------------------------

    if not cms_result.get("detected"):
        score += 20

    elif cms_result.get("name") in [
        "Shopify",
        "Wix",
        "Squarespace"
    ]:
        score += 18

    else:
        score += 15

    # -------------------------
    # Final Score
    # -------------------------

    return max(0, min(score, 100))