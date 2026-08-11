from datetime import datetime, timezone

from scanner.header_checker import check_headers
from scanner.ssl_checker import check_ssl
from scanner.cms_detector import detect_cms
from scanner.advanced_scoring import calculate_overall_score
from scanner.risk import calculate_risk


def run_scan(url: str) -> dict:
    """
    Run all passive security checks and return
    a unified security report.
    """

    # -------------------------
    # Run Header Analysis
    # -------------------------

    header_result = check_headers(url)

    if "error" in header_result:

        raw_error = str(header_result["error"])

        # Friendly error messages for common connection problems

        if (
            "NameResolutionError" in raw_error
            or "Failed to resolve" in raw_error
            or "getaddrinfo failed" in raw_error
        ):
            user_error = (
                "Unable to reach the website. "
                "Please check that the domain exists "
                "and the URL is correct."
            )

        elif (
            "ConnectionError" in raw_error
            or "Max retries exceeded" in raw_error
        ):
            user_error = (
                "Unable to connect to the website. "
                "Please check the URL and try again."
            )

        elif "timed out" in raw_error.lower():
            user_error = (
                "The website did not respond within "
                "the allowed time."
            )

        else:
            user_error = (
                "Unable to retrieve the website. "
                "Please check the URL and try again."
            )

        return {
            "success": False,
            "error": user_error
        }

    # -------------------------
    # Run SSL Inspection
    # -------------------------

    ssl_result = check_ssl(url)

    # -------------------------
    # Run CMS Detection
    # -------------------------

    cms_result = detect_cms(url)

    # -------------------------
    # Calculate Overall Score
    # -------------------------

    overall_score = calculate_overall_score(
        header_result,
        ssl_result,
        cms_result
    )

    # -------------------------
    # Calculate Risk Level
    # -------------------------

    risk_level = calculate_risk(overall_score)

    # -------------------------
    # Build Executive Summary
    # -------------------------

    if header_result["failed_checks"]:

        recommendation = (
            "Review the failed security headers "
            "to improve your security score."
        )

    elif not ssl_result.get("enabled"):

        recommendation = (
            "Enable HTTPS and configure a valid "
            "SSL/TLS certificate."
        )

    elif not ssl_result.get("valid"):

        recommendation = (
            "Review the SSL/TLS certificate and "
            "resolve any certificate issues."
        )

    else:

        recommendation = (
            "No immediate security issues were "
            "detected by the passive checks."
        )

    # -------------------------
    # Build Final Report
    # -------------------------

    report = {
        "success": True,

        "url": header_result["url"],

        "timestamp": (
            datetime.now(timezone.utc)
            .isoformat(timespec="seconds")
            .replace("+00:00", "Z")
        ),

        "overall_score": overall_score,

        "grade": (
    		"A" if overall_score >= 90 else
    		"B" if overall_score >= 80 else
    		"C" if overall_score >= 70 else
    		"D" if overall_score >= 60 else
    		"F"
	),

        "risk_level": risk_level,

        "summary": {
            "passed_checks": len(
                header_result["passed_checks"]
            ),

            "failed_checks": len(
                header_result["failed_checks"]
            ),

            "ssl_enabled": ssl_result.get(
                "enabled",
                False
            ),

            "cms_detected": cms_result.get(
                "detected",
                False
            ),

            "recommendation": recommendation
        },

        "headers": {
            "passed_checks": header_result[
                "passed_checks"
            ],

            "failed_checks": header_result[
                "failed_checks"
            ]
        },

        "ssl": ssl_result,

        "cms": cms_result
    }

    return report