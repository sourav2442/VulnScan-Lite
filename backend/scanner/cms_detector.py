import re
import requests
from bs4 import BeautifulSoup


def detect_cms(url):
    """
    Detect CMS using passive HTML and HTTP header analysis.
    """

    try:
        response = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent": "VulnScan-Lite/1.0"
            }
        )

        soup = BeautifulSoup(response.text, "html.parser")

        # -------------------------
        # Meta Generator Detection
        # -------------------------

        generator = soup.find("meta", attrs={"name": "generator"})

        if generator:

            content = generator.get("content", "")

            cms_patterns = [
                "WordPress",
                "Drupal",
                "Joomla",
                "Ghost"
            ]

            for cms in cms_patterns:

                if cms.lower() in content.lower():

                    version = None

                    match = re.search(r"\d+(\.\d+)+", content)

                    if match:
                        version = match.group()

                    return {
                        "detected": True,
                        "name": cms,
                        "version": version
                    }

        # -------------------------
        # HTTP Header Detection
        # -------------------------

        powered_by = response.headers.get("X-Powered-By", "")

        if powered_by:

            return {
                "detected": True,
                "name": powered_by,
                "version": None
            }

        # -------------------------
        # HTML Pattern Detection
        # -------------------------

        html = response.text.lower()

        if "wp-content" in html:
            return {
                "detected": True,
                "name": "WordPress",
                "version": None
            }

        if "cdn.shopify.com" in html:
            return {
                "detected": True,
                "name": "Shopify",
                "version": None
            }

        if "wixstatic.com" in html:
            return {
                "detected": True,
                "name": "Wix",
                "version": None
            }

        if "static.squarespace.com" in html:
            return {
                "detected": True,
                "name": "Squarespace",
                "version": None
            }

        return {
            "detected": False,
            "name": "Unknown",
            "version": None
        }

    except Exception as e:

        return {
            "error": str(e)
        }