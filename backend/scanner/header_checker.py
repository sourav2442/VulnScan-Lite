import requests

SECURITY_HEADERS = [
    "Content-Security-Policy",
    "X-Frame-Options",
    "Strict-Transport-Security",
    "X-Content-Type-Options",
    "Referrer-Policy",
    "Permissions-Policy"
]


def check_headers(url):
    """
    Checks whether common security headers are present.
    Returns a dictionary containing the scan results.
    """

    try:
        response = requests.get(
            url,
            timeout=10,
            allow_redirects=True,
            headers={
                "User-Agent": "VulnScan-Lite/1.0"
            }
        )

        results = {
            "url": response.url,
            "status_code": response.status_code,
            "headers": {}
        }

        for header in SECURITY_HEADERS:
            results["headers"][header] = header in response.headers

        return results

    except requests.exceptions.RequestException as e:
        return {
            "error": str(e)
        }