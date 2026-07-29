from datetime import datetime

from scanner.header_checker import check_headers
from scanner.ssl_checker import check_ssl
from scanner.cms_detector import detect_cms
from scanner.advanced_scoring import calculate_overall_score
from scanner.risk import calculate_risk


def run_scan(url: str) -> dict:
    """
    Runs all passive security checks and returns
    a unified security report.
    """

    # -------------------------
    # Run Header Analysis
    # -------------------------
    header_result = check_headers(url)

    if "error" in header_result:
        return {
            "success": False,
            "error": header_result["error"]
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
    recommendation = (
        "Review failed security headers to improve your score."
        if header_result["failed_checks"]
        else "No immediate issues detected."
    )

    # -------------------------
    # Build Final Report
    # -------------------------
    report = {
        "success": True,

        "url": header_result["url"],

        "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",

        "overall_score": overall_score,

        # We'll improve grade calculation later
        "grade": header_result["grade"],

        "risk_level": risk_level,

        "summary": {
            "passed_checks": len(header_result["passed_checks"]),
            "failed_checks": len(header_result["failed_checks"]),
            "ssl_enabled": ssl_result.get("enabled", False),
            "cms_detected": cms_result.get("detected", False),
            "recommendation": recommendation
        },

        "headers": {
            "passed_checks": header_result["passed_checks"],
            "failed_checks": header_result["failed_checks"]
        },

        "ssl": ssl_result,

        "cms": cms_result
    }

    return report