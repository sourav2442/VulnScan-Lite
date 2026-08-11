from urllib.parse import urlparse


def validate_and_normalize_url(url: str):
    """
    Validate and normalize a user-provided website URL.

    Returns:
        (normalized_url, None) on success
        (None, error_message) on failure
    """

    if not isinstance(url, str):
        return None, "Please enter a valid website URL."

    url = url.strip()

    if not url:
        return None, "Please enter a website URL."

    # Remove accidental surrounding quotes
    url = url.strip("\"'")

    if not url:
        return None, "Please enter a website URL."

    # ---------------------------------------------------------
    # Automatically add HTTPS for bare domains
    # Example:
    # github.com -> https://github.com
    # ---------------------------------------------------------

    if "://" not in url:
        url = "https://" + url

    try:
        parsed = urlparse(url)
    except Exception:
        return None, "The URL format is invalid."

    # ---------------------------------------------------------
    # Protocol validation
    # ---------------------------------------------------------

    if parsed.scheme.lower() not in ("http", "https"):
        return (
            None,
            "Unsupported protocol. Please use http:// or https://."
        )

    # ---------------------------------------------------------
    # Host validation
    # ---------------------------------------------------------

    if not parsed.netloc:
        return None, "The URL must contain a valid domain name."

    hostname = parsed.hostname

    if not hostname:
        return None, "The URL must contain a valid domain name."

    # Reject whitespace
    if any(char.isspace() for char in url):
        return None, "The URL cannot contain spaces."

    # Reject localhost/internal addresses for this scanner
    # This keeps VulnScan Lite focused on public websites.
    hostname_lower = hostname.lower()

    blocked_hosts = {
        "localhost",
        "127.0.0.1",
        "0.0.0.0",
        "::1",
    }

    if hostname_lower in blocked_hosts:
        return (
            None,
            "Localhost and internal addresses cannot be scanned."
        )

    # ---------------------------------------------------------
    # Basic domain validation
    # ---------------------------------------------------------

    if "." not in hostname and hostname_lower != "localhost":
        return (
            None,
            "Please enter a valid public domain, such as example.com."
        )

    # ---------------------------------------------------------
    # Normalize URL
    # ---------------------------------------------------------

    normalized_url = url.rstrip("/")

    return normalized_url, None