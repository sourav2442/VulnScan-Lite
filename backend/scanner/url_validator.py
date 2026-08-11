from urllib.parse import urlparse


def validate_url(url: str) -> tuple[bool, str]:
    """
    Validate a URL before sending a request.

    Returns:
        (True, "") when the URL is valid.
        (False, error_message) when the URL is invalid.
    """

    if not isinstance(url, str):
        return False, "URL must be a string."

    url = url.strip()

    if not url:
        return False, "URL cannot be empty."

    if len(url) > 2048:
        return False, "URL is too long."

    parsed = urlparse(url)

    # Only allow HTTP and HTTPS.
    if parsed.scheme.lower() not in ("http", "https"):
        return False, "URL must start with http:// or https://."

    # A hostname is required.
    if not parsed.hostname:
        return False, "URL must contain a valid hostname."

    # Reject URLs containing whitespace.
    if any(character.isspace() for character in url):
        return False, "URL cannot contain spaces."

    return True, ""