from flask import Flask, request, jsonify
from flask_cors import CORS
from rq.job import Job

from rq_queue import scan_queue
from tasks.scan_tasks import scan_website


app = Flask(__name__)

CORS(app, resources={
    r"/scan*": {
        "origins": [
            "http://localhost:5173",
            "http://127.0.0.1:5173"
        ]
    }
})


@app.route("/")
def home():
    return jsonify({
        "project": "VulnScan Lite",
        "status": "Running",
        "version": "1.0"
    })


@app.route("/scan", methods=["POST"])
def scan():

    data = request.get_json()

    if not data or "url" not in data:
        return jsonify({
            "success": False,
            "error": "Please provide a URL."
        }), 400

    url = data["url"].strip()

    if not url:
        return jsonify({
            "success": False,
            "error": "URL cannot be empty."
        }), 400

    job = scan_queue.enqueue(
        scan_website,
        url,
        result_ttl=3600,
        failure_ttl=3600
    )

    return jsonify({
        "success": True,
        "scan_id": job.id,
        "status": "queued"
    }), 202


@app.route("/scan/<job_id>/status", methods=["GET"])
def scan_status(job_id):

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

    response = {
        "success": True,
        "scan_id": job.id,
        "status": job.get_status()
    }

    if job.is_finished:
        response["result"] = job.result

    elif job.is_failed:
        response["error"] = "Scan failed."

    return jsonify(response)


if __name__ == "__main__":
    app.run(
        debug=True,
        port=5001
    )