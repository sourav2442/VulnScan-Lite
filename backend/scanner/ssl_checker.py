import ssl
import socket
from datetime import datetime, timezone
from urllib.parse import urlparse


SSL_TIMEOUT = 10


def check_ssl(url: str) -> dict:
    """
    Check SSL/TLS certificate information for a website.

    Returns a structured result that can be consumed by
    the scanner engine and frontend.
    """

    try:
        # -------------------------
        # Parse URL
        # -------------------------

        parsed_url = urlparse(url)

        hostname = parsed_url.hostname
        scheme = parsed_url.scheme.lower()

        if not hostname:
            return {
                "enabled": False,
                "valid": False,
                "error": "Invalid URL: hostname is missing."
            }

        # -------------------------
        # HTTP websites
        # -------------------------

        if scheme != "https":
            return {
                "enabled": False,
                "valid": False,
                "issuer": "N/A",
                "subject": hostname,
                "expires": "N/A",
                "days_remaining": None,
                "error": "SSL/TLS is not enabled because the URL does not use HTTPS."
            }

        # -------------------------
        # Determine HTTPS port
        # -------------------------

        port = parsed_url.port or 443

        # -------------------------
        # Create SSL context
        # -------------------------

        context = ssl.create_default_context()

        # -------------------------
        # Connect to server
        # -------------------------

        with socket.create_connection(
            (hostname, port),
            timeout=SSL_TIMEOUT
        ) as sock:

            with context.wrap_socket(
                sock,
                server_hostname=hostname
            ) as secure_sock:

                certificate = secure_sock.getpeercert()

        # -------------------------
        # Certificate validation
        # -------------------------

        if not certificate:
            return {
                "enabled": True,
                "valid": False,
                "issuer": "Unknown",
                "subject": hostname,
                "expires": "Unknown",
                "days_remaining": None,
                "error": "No SSL certificate information was returned."
            }

        # -------------------------
        # Certificate expiry
        # -------------------------

        not_after = certificate.get("notAfter")

        if not not_after:
            return {
                "enabled": True,
                "valid": False,
                "issuer": "Unknown",
                "subject": hostname,
                "expires": "Unknown",
                "days_remaining": None,
                "error": "Certificate expiry information is unavailable."
            }

        expiry_date = datetime.strptime(
            not_after,
            "%b %d %H:%M:%S %Y %Z"
        ).replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)

        days_remaining = (
            expiry_date - now
        ).days

        # -------------------------
        # Certificate issuer
        # -------------------------

        issuer_data = certificate.get("issuer", [])

        issuer = dict(
            item[0]
            for item in issuer_data
            if item
        )

        # -------------------------
        # Certificate subject
        # -------------------------

        subject_data = certificate.get("subject", [])

        subject = dict(
            item[0]
            for item in subject_data
            if item
        )

        # -------------------------
        # Final result
        # -------------------------

        return {
            "enabled": True,
            "valid": days_remaining > 0,
            "issuer": issuer.get(
                "organizationName",
                "Unknown"
            ),
            "subject": subject.get(
                "commonName",
                hostname
            ),
            "expires": expiry_date.strftime(
                "%Y-%m-%d"
            ),
            "days_remaining": days_remaining
        }

    # -------------------------
    # Connection errors
    # -------------------------

    except socket.timeout:
        return {
            "enabled": False,
            "valid": False,
            "error": "SSL/TLS connection timed out."
        }

    except ConnectionRefusedError:
        return {
            "enabled": False,
            "valid": False,
            "error": "The HTTPS connection was refused."
        }

    except ssl.SSLCertVerificationError:
        return {
            "enabled": True,
            "valid": False,
            "error": (
                "The SSL certificate could not be verified."
            )
        }

    except ssl.SSLError:
        return {
            "enabled": True,
            "valid": False,
            "error": (
                "An SSL/TLS error occurred while "
                "checking the certificate."
            )
        }

    except socket.gaierror:
        return {
            "enabled": False,
            "valid": False,
            "error": (
                "Unable to resolve the website hostname."
            )
        }

    except ValueError:
        return {
            "enabled": False,
            "valid": False,
            "error": "Invalid URL or port."
        }

    except OSError:
        return {
            "enabled": False,
            "valid": False,
            "error": (
                "Unable to establish an SSL/TLS connection."
            )
        }

    except Exception:
        return {
            "enabled": False,
            "valid": False,
            "error": (
                "An unexpected error occurred while "
                "checking SSL/TLS."
            )
        }