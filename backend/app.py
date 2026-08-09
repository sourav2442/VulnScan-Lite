from flask import Flask, request, jsonify
from flask_cors import CORS
from rq.job import Job
from urllib.parse import urlparse

from rq_queue import scan_queue

app = Flask(__name__)

# Allow the React frontend running on port 5173
# to communicate with the Flask backend.
CORS(app)


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "project": "VulnScan Lite",
        "status": "Running",
        "version": "1.0"
    })


def validate_url(url):
    """
    Validate that the supplied value is a proper HTTP/HTTPS URL.
    """

    if not url:
        return False, "URL cannot be empty."

    url = str(url).strip()

    try:
        parsed = urlparse(url)
    except Exception:
        return False, "Invalid URL."

    # Only allow HTTP and HTTPS.
    if parsed.scheme not in ("http", "https"):
        return False, "URL must start with http:// or https://."

    # A hostname is required.
    if not parsed.netloc:
        return False, "Please provide a valid website URL."

    # Reject URLs such as https://
    if not parsed.hostname:
        return False, "Please provide a valid website hostname."

    return True, url


@app.route("/scan", methods=["POST"])
def start_scan():
    """
    Start a new vulnerability scan.

    Expected JSON:
    {
        "url": "https://example.com"
    }
    """

    data = request.get_json(silent=True)

    if not data or "url" not in data:
        return jsonify({
            "success": False,
            "error": "Please provide a URL."
        }), 400

    url = str(data["url"]).strip()

    # Validate URL before adding it to the queue.
    valid, message = validate_url(url)

    if not valid:
        return jsonify({
            "success": False,
            "error": message
        }), 400

    # Add the scan task to the RQ queue.
    job = scan_queue.enqueue(
        "tasks.scan_tasks.scan_website",
        url
    )

    return jsonify({
        "success": True,
        "scan_id": job.id,
        "status": "queued"
    }), 202


@app.route("/scan/<job_id>/status", methods=["GET"])
def scan_status(job_id):
    """
    Return the current status/result of a scan.
    """

    try:
        job = Job.fetch(
            job_id,
            connection=scan_queue.connection
        )

    except Exception:
        return jsonify({
            "success": False,
            "error": "Scan job not found."
        }), 404

    status = job.get_status()

    response = {
        "success": True,
        "scan_id": job.id,
        "status": status
    }

    # RQ uses "finished" when the job completed successfully.
    if status == "finished":
        response["result"] = job.result

    # RQ uses "failed" when the task raised an exception.
    elif status == "failed":
        response["error"] = (
            str(job.exc_info)
            if job.exc_info
            else "Scan failed."
        )

    return jsonify(response), 200


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5001,
        debug=True
    )