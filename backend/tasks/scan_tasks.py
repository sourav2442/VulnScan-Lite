from celery_app import celery
from scanner.scanner_engine import run_scan


@celery.task
def scan_website(url):
    """
    Background Celery task that runs the VulnScan Lite scanner.
    """
    return run_scan(url)