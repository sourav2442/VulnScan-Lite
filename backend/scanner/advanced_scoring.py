def calculate_overall_score(header_result, ssl_result, cms_result):
    """
    Calculate the overall security score using weighted scoring.
    """

    score = 0

    # -------------------------
    # Header Score (50 Points)
    # -------------------------

    total_headers = (
        len(header_result["passed_checks"]) +
        len(header_result["failed_checks"])
    )

    if total_headers > 0:
        score += round(
            (len(header_result["passed_checks"]) / total_headers) * 50
        )

    # -------------------------
    # SSL Score (30 Points)
    # -------------------------

    if ssl_result.get("enabled") and ssl_result.get("valid"):

        days = ssl_result.get("days_remaining", 0)

        if days > 90:
            score += 30
        elif days > 30:
            score += 25
        elif days > 7:
            score += 15
        else:
            score += 5

    # -------------------------
    # CMS Score (20 Points)
    # -------------------------

    if not cms_result.get("detected"):
        score += 20

    elif cms_result["name"] in ["Shopify", "Wix", "Squarespace"]:
        score += 18

    else:
        score += 15

    return min(score, 100)