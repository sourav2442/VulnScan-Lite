# =========================================================
# GENERATE SECURITY REPORT
# =========================================================

@app.route("/scan/<scan_id>/report", methods=["GET"])
def generate_report(scan_id):

    try:

        # -------------------------------------------------
        # Get Celery task
        # -------------------------------------------------

        task = AsyncResult(
            scan_id,
            app=celery
        )

        # -------------------------------------------------
        # Scan is still running
        # -------------------------------------------------

        if not task.successful():

            if task.failed():

                return jsonify({
                    "success": False,
                    "error": "Scan failed. Report cannot be generated."
                }), 500

            return jsonify({
                "success": False,
                "error": "Scan is not completed yet."
            }), 409

        # -------------------------------------------------
        # Get scan result
        # -------------------------------------------------

        result = task.result

        if not isinstance(result, dict):

            return jsonify({
                "success": False,
                "error": "Invalid scan result."
            }), 500

        if result.get("success") is False:

            return jsonify({
                "success": False,
                "error": result.get(
                    "error",
                    "Scan failed."
                )
            }), 400

        # -------------------------------------------------
        # Generate PDF
        # -------------------------------------------------

        pdf_buffer = generate_security_report(
            result
        )

        # -------------------------------------------------
        # Generate filename
        # -------------------------------------------------

        score = result.get(
            "overall_score",
            "report"
        )

        filename = (
            f"VulnScan_Lite_Security_Report_"
            f"{score}.pdf"
        )

        # -------------------------------------------------
        # Send PDF
        # -------------------------------------------------

        return send_file(
            pdf_buffer,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:

        print(
            "REPORT GENERATION ERROR:",
            repr(e)
        )

        return jsonify({
            "success": False,
            "error": "Unable to generate security report."
        }), 500