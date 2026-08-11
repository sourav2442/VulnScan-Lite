from flask import Flask, request, jsonify
from flask_cors import CORS
from celery.result import AsyncResult
from celery_app import celery
from tasks.scan_tasks import scan_website

from scanner.url_validator import validate_and_normalize_url


# =========================================================
# FLASK APPLICATION
# =========================================================

app = Flask(__name__)

# Allow the React frontend to communicate with Flask
CORS(app)


# =========================================================
# HOME ROUTE
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

        # -------------------------------------------------
        # Read JSON request
        # -------------------------------------------------

        data = request.get_json(silent=True) or {}

        url = data.get("url", "")

        # -------------------------------------------------
        # Validate and normalize URL
        # -------------------------------------------------

        normalized_url, validation_error = (
            validate_and_normalize_url(url)
        )

        if validation_error:

            return jsonify({
                "success": False,
                "error": validation_error
            }), 400

        # -------------------------------------------------
        # Create background scan job
        # -------------------------------------------------

        task = scan_website.delay(normalized_url)

        # -------------------------------------------------
        # Return scan ID
        # -------------------------------------------------

        return jsonify({
            "success": True,
            "scan_id": task.id,
            "status": "queued"
        }), 200

    except Exception as e:

        print("START SCAN ERROR:", repr(e))

        return jsonify({
            "success": False,
            "error": "Unable to start the scan."
        }), 500


# =========================================================
# SCAN STATUS
# =========================================================

@app.route("/scan/<scan_id>/status", methods=["GET"])
def scan_status(scan_id):

    try:

        # -------------------------------------------------
        # Get Celery task
        # -------------------------------------------------

        task = AsyncResult(scan_id, app=celery)

        # -------------------------------------------------
        # Task completed
        # -------------------------------------------------

        if task.successful():

            result = task.result

            # Safety check
            if not isinstance(result, dict):

                return jsonify({
                    "success": False,
                    "status": "failed",
                    "error": "Invalid scan result returned by worker."
                }), 500

            # Scanner itself may report success=False
            if result.get("success") is False:

                return jsonify({
                    "success": False,
                    "status": "failed",
                    "error": result.get(
                        "error",
                        "Scan failed."
                    )
                }), 200

            return jsonify({
                "success": True,
                "status": "completed",
                "result": result
            }), 200

        # -------------------------------------------------
        # Task failed
        # -------------------------------------------------

        if task.failed():

            return jsonify({
                "success": False,
                "status": "failed",
                "error": "Scan worker failed."
            }), 500

        # -------------------------------------------------
        # Task is still running
        # -------------------------------------------------

        if task.state in ("PENDING", "RECEIVED"):

            return jsonify({
                "success": True,
                "status": "queued"
            }), 200

        if task.state in ("STARTED", "RETRY"):

            return jsonify({
                "success": True,
                "status": "running"
            }), 200

        # -------------------------------------------------
        # Unknown Celery state
        # -------------------------------------------------

        return jsonify({
            "success": True,
            "status": task.state.lower()
        }), 200

    except Exception as e:

        print("SCAN STATUS ERROR:", repr(e))

        return jsonify({
            "success": False,
            "status": "failed",
            "error": "Unable to retrieve scan status."
        }), 500


# =========================================================
# ERROR HANDLERS
# =========================================================

@app.errorhandler(404)
def not_found(error):

    return jsonify({
        "success": False,
        "error": "API endpoint not found."
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):

    return jsonify({
        "success": False,
        "error": "HTTP method not allowed."
    }), 405


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5001,
        debug=True
    )