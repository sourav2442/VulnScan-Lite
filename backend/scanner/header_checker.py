import requests

from scanner.header_data import SECURITY_HEADERS
from scanner.scoring import calculate_score


def check_headers(url):

    try:

        response = requests.get(
            url,
            timeout=10,
            allow_redirects=True,
            headers={
                "User-Agent": "VulnScan-Lite/1.0"
            }
        )

        passed = []
        failed = []

        for header, info in SECURITY_HEADERS.items():

            if header in response.headers:

                passed.append({
                    "header": header,
                    "severity": info["severity"],
                    "description": info["description"]
                })

            else:

                failed.append({
                    "header": header,
                    "severity": info["severity"],
                    "description": info["description"],
                    "recommendation": info["recommendation"]
                })

        score, grade = calculate_score(
            len(passed),
            len(SECURITY_HEADERS)
        )

        return {

            "url": response.url,

            "status_code": response.status_code,

            "score": score,

            "grade": grade,

            "passed_checks": passed,

            "failed_checks": failed

        }

    except requests.exceptions.RequestException as e:

        return {
            "error": str(e)
        }