from flask import Flask, request, jsonify
from flask_cors import CORS
from threading import Thread
from uuid import uuid4

from scanner.scanner_engine import run_scan

# =========================================================
# FLASK APPLICATION
# =========================================================

app = Flask(__name__)
CORS(app)

# =========================================================
# IN-MEMORY SCAN STORAGE
# =========================================================

scan_jobs = {}


# =========================================================
# BACKGROUND SCAN WORKER
# =========================================================

def execute_scan(scan_id, url):
    """
    Run the vulnerability scan in a background thread.
    """

    try:
        scan_jobs[scan_id]["status"] = "running"

        result = run_scan(url)

        if result.get("success"):
            scan_jobs[scan_id]["status"] = "completed"
            scan_jobs[scan_id]["result"] = result
        else:
            scan_jobs[scan_id]["status"] = "failed"
            scan_jobs[scan_id]["error"] = result.get(
                "error",
                "Scan failed."
            )

    except Exception as exc:
        scan_jobs[scan_id]["status"] = "failed"
        scan_jobs[scan_id]["error"] = str(exc)


# =========================================================
# HOME
# =========================================================

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "success": True,
        "message": "VulnScan Lite API is running.",
        "service": "Passive Web Vulnerability Scanner"
    })


# =========================================================
# START SCAN
# =========================================================

@app.route("/scan", methods=["POST"])
def start_scan():

    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                "success": False,
                "error": "Request body is required."
            }), 400

        url = data.get("url", "").strip()

        if not url:
            return jsonify({
                "success": False,
                "error": "URL is required."
            }), 400

        # -------------------------------------------------
        # Normalize URL
        # -------------------------------------------------

        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        # -------------------------------------------------
        # Generate scan ID
        # -------------------------------------------------

        scan_id = str(uuid4())

        # -------------------------------------------------
        # Create job
        # -------------------------------------------------

        scan_jobs[scan_id] = {
            "status": "queued",
            "result": None,
            "error": None,
            "url": url
        }

        # -------------------------------------------------
        # Start background scan
        # -------------------------------------------------

        worker = Thread(
            target=execute_scan,
            args=(scan_id, url),
            daemon=True
        )

        worker.start()

        return jsonify({
            "success": True,
            "scan_id": scan_id,
            "status": "queued"
        }), 200

    except Exception as exc:

        print("START SCAN ERROR:", exc)

        return jsonify({
            "success": False,
            "error": "Unable to start the scan."
        }), 500


# =========================================================
# SCAN STATUS
# =========================================================

@app.route("/scan/<scan_id>/status", methods=["GET"])
def scan_status(scan_id):

    job = scan_jobs.get(scan_id)

    if not job:
        return jsonify({
            "success": False,
            "error": "Scan job not found."
        }), 404

    # -----------------------------------------------------
    # QUEUED
    # -----------------------------------------------------

    if job["status"] == "queued":

        return jsonify({
            "success": True,
            "status": "queued"
        }), 200

    # -----------------------------------------------------
    # RUNNING
    # -----------------------------------------------------

    if job["status"] == "running":

        return jsonify({
            "success": True,
            "status": "running"
        }), 200

    # -----------------------------------------------------
    # FAILED
    # -----------------------------------------------------

    if job["status"] == "failed":

        return jsonify({
            "success": False,
            "status": "failed",
            "error": job.get(
                "error",
                "Scan failed."
            )
        }), 200

    # -----------------------------------------------------
    # COMPLETED
    # -----------------------------------------------------

    if job["status"] == "completed":

        return jsonify({
            "success": True,
            "status": "completed",
            "result": job["result"]
        }), 200

    # -----------------------------------------------------
    # UNKNOWN
    # -----------------------------------------------------

    return jsonify({
        "success": False,
        "status": "unknown",
        "error": "Unknown scan status."
    }), 500


# =========================================================
# RUN SERVER
# =========================================================

if __name__ == "__main__":

    print("=" * 60)
    print("VULNSCAN LITE")
    print("Passive Web Vulnerability Scanner")
    print("=" * 60)
    print("Backend: http://127.0.0.1:5001")
    print("=" * 60)

    app.run(
        host="127.0.0.1",
        port=5001,
        debug=True,
        use_reloader=False
    )