import ssl
import socket
from datetime import datetime
from urllib.parse import urlparse


def check_ssl(url):
    """
    Checks SSL certificate information for a website.
    """

    try:
        parsed_url = urlparse(url)

        hostname = parsed_url.hostname

        if hostname is None:
            return {
                "enabled": False,
                "error": "Invalid URL."
            }

        context = ssl.create_default_context()

        with socket.create_connection((hostname, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as secure_sock:

                certificate = secure_sock.getpeercert()

        expiry_date = datetime.strptime(
            certificate["notAfter"],
            "%b %d %H:%M:%S %Y %Z"
        )

        days_remaining = (expiry_date - datetime.utcnow()).days

        issuer = dict(x[0] for x in certificate["issuer"])

        subject = dict(x[0] for x in certificate["subject"])

        return {

            "enabled": True,

            "valid": days_remaining > 0,

            "issuer": issuer.get("organizationName", "Unknown"),

            "subject": subject.get("commonName", hostname),

            "expires": expiry_date.strftime("%Y-%m-%d"),

            "days_remaining": days_remaining

        }

    except Exception as e:

        return {

            "enabled": False,

            "error": str(e)

        }