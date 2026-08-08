from scanner.scanner_engine import run_scan


def scan_website(url):
    """
    Background RQ job that runs the VulnScan Lite scanner.
    """
    return run_scan(url)