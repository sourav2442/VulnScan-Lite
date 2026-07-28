from datetime import datetime

from scanner.header_checker import check_headers
from scanner.ssl_checker import check_ssl
from scanner.cms_detector import detect_cms


def run_scan(url: str) -> dict:
    """
    Runs all passive security checks and combines the results.
    """

    header_result = check_headers(url)

    # If we can't even reach the website, stop here.
    if "error" in header_result:
        return {
            "success": False,
            "error": header_result["error"]
        }

    ssl_result = check_ssl(url)
    cms_result = detect_cms(url)

    report = {
        "success": True,
        "url": header_result["url"],
        "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",

        "overall_score": header_result["score"],
        "grade": header_result["grade"],

        "summary": {
            "passed_checks": len(header_result["passed_checks"]),
            "failed_checks": len(header_result["failed_checks"])
        },

        "headers": {
            "passed_checks": header_result["passed_checks"],
            "failed_checks": header_result["failed_checks"]
        },

        "ssl": ssl_result,

        "cms": cms_result
    }

    return report