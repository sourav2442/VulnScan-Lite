from flask import Flask, request, jsonify
from scanner.scanner_engine import run_scan

app = Flask(__name__)


@app.route("/")
def home():
    return {
        "project": "VulnScan Lite",
        "status": "Running"
    }


@app.route("/scan")
def scan():

    url = request.args.get("url")

    if not url:
        return jsonify({
            "error": "Please provide a URL."
        }), 400

    result = run_scan(url)
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)