import { useState } from "react";
import "./App.css";

const API_BASE = "http://127.0.0.1:5001";

function App() {
  const [url, setUrl] = useState("");
  const [scanning, setScanning] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  // =========================================================
  // START SCAN
  // =========================================================

  const startScan = async (e) => {
    e.preventDefault();

    if (!url.trim()) {
      setError("Please enter a website URL.");
      return;
    }

    setScanning(true);
    setResult(null);
    setError("");

    try {
      const response = await fetch(`${API_BASE}/scan`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          url: url.trim(),
        }),
      });

      const data = await response.json();

      console.log("SCAN START RESPONSE:", data);

      if (!response.ok || !data.success) {
        throw new Error(
          data.error || "Unable to start scan."
        );
      }

      const scanId = data.scan_id;

      if (!scanId) {
        throw new Error(
          "Server did not return a scan ID."
        );
      }

      console.log("SCAN ID:", scanId);

      await pollScanStatus(scanId);

    } catch (err) {
      console.error("SCAN ERROR:", err);

      setError(
        err.message || "Something went wrong."
      );

      setScanning(false);
    }
  };


  // =========================================================
  // POLL SCAN STATUS
  // =========================================================

  const pollScanStatus = async (scanId) => {
    let attempts = 0;

    // 60 attempts × 1 second = 60 seconds
    const maxAttempts = 60;

    const checkStatus = async () => {
      try {
        const response = await fetch(
          `${API_BASE}/scan/${scanId}/status`,
          {
            method: "GET",
            headers: {
              "Accept": "application/json",
            },
          }
        );

        const data = await response.json();

        console.log(
          `SCAN STATUS [${attempts + 1}]:`,
          data
        );

        if (!response.ok) {
          throw new Error(
            data.error ||
            "Unable to check scan status."
          );
        }


        // =====================================================
        // IMPORTANT:
        // Backend may return the completed result directly
        // without status = "completed".
        //
        // Your PowerShell response showed:
        //
        // {
        //   result: {
        //      grade: "A",
        //      overall_score: 87,
        //      ...
        //   }
        // }
        //
        // So we check for data.result first.
        // =====================================================

        if (
          data.result &&
          typeof data.result === "object"
        ) {
          console.log(
            "SCAN COMPLETED - RESULT RECEIVED:",
            data.result
          );

          setResult(data.result);
          setScanning(false);
          setError("");

          return;
        }


        // =====================================================
        // Some backend versions may return the scan result
        // directly instead of inside "result".
        // =====================================================

        if (
          data.success === true &&
          data.overall_score !== undefined
        ) {
          console.log(
            "SCAN COMPLETED - DIRECT RESULT:",
            data
          );

          setResult(data);
          setScanning(false);
          setError("");

          return;
        }


        // =====================================================
        // FAILED
        // =====================================================

        if (
          data.status === "failed" ||
          data.success === false
        ) {
          throw new Error(
            data.error ||
            "Scan failed."
          );
        }


        // =====================================================
        // STILL RUNNING
        // =====================================================

        attempts++;

        if (attempts >= maxAttempts) {
          throw new Error(
            "Scan timed out. Please try again."
          );
        }

        setTimeout(checkStatus, 1000);

      } catch (err) {
        console.error(
          "STATUS ERROR:",
          err
        );

        setError(
          err.message ||
          "Unable to retrieve scan result."
        );

        setScanning(false);
      }
    };

    checkStatus();
  };


  // =========================================================
  // RESET
  // =========================================================

  const resetScan = () => {
    setUrl("");
    setResult(null);
    setError("");
    setScanning(false);
  };


  // =========================================================
  // RESULT DATA
  // =========================================================

  const passedChecks =
    result?.headers?.passed_checks || [];

  const failedChecks =
    result?.headers?.failed_checks || [];

  const ssl =
    result?.ssl || {};

  const cms =
    result?.cms || {};

  const summary =
    result?.summary || {};


  // =========================================================
  // MAIN UI
  // =========================================================

  return (
    <div className="app">

      {/* =====================================================
          HEADER
      ===================================================== */}

      <header className="topbar">

        <div className="brand">

          <div className="brand-icon">
            V
          </div>

          <div className="brand-text">

            <h1>
              VulnScan Lite
            </h1>

            <p>
              Passive Web Security Scanner
            </p>

          </div>

        </div>


        <div className="status-indicator">

          <span className="status-dot"></span>

          Scanner Online

        </div>

      </header>


      {/* =====================================================
          MAIN
      ===================================================== */}

      <main className="container">


        {/* ===================================================
            HOME / SCAN SECTION
        =================================================== */}

        {!result && (

          <section className="hero-section">

            <div className="hero-content">

              <span className="hero-badge">
                WEB SECURITY ANALYSIS
              </span>


              <h2>

                Check your website's

                <span>
                  security posture.
                </span>

              </h2>


              <p className="hero-description">

                VulnScan Lite performs passive security
                checks for HTTP security headers,
                SSL/TLS configuration and CMS information.

              </p>


              <form
                className="scan-form"
                onSubmit={startScan}
              >

                <input
                  type="text"
                  value={url}
                  onChange={(e) =>
                    setUrl(e.target.value)
                  }
                  placeholder="https://example.com"
                  disabled={scanning}
                />


                <button
                  type="submit"
                  disabled={scanning}
                >

                  {scanning
                    ? "Scanning..."
                    : "Scan Website"}

                </button>

              </form>


              {/* SCANNING */}

              {scanning && (

                <div className="scan-status">

                  <span className="loading-dot"></span>

                  Scanning website. Please wait...

                </div>

              )}


              {/* ERROR */}

              {error && (

                <div className="error-message">

                  {error}

                </div>

              )}

            </div>

          </section>

        )}


        {/* ===================================================
            RESULTS
        =================================================== */}

        {result && (

          <section className="results-section">


            {/* RESULTS HEADER */}

            <div className="results-header">

              <div>

                <span className="hero-badge">
                  SECURITY REPORT
                </span>


                <h2>
                  Security Health Report
                </h2>


                <p className="scanned-url">
                  {result.url}
                </p>

              </div>


              <button
                className="new-scan-button"
                onClick={resetScan}
              >
                + New Scan
              </button>

            </div>


            {/* =================================================
                SCORE SECTION
            ================================================= */}

            <div className="score-section">


              {/* SCORE CARD */}

              <div className="score-card">

                <div className="score-label">
                  OVERALL SECURITY SCORE
                </div>


                <div className="score-number">

                  {result.overall_score ?? 0}

                  <span>
                    /100
                  </span>

                </div>


                <div className="grade">

                  Grade {result.grade || "N/A"}

                </div>


                <p className="score-description">

                  Overall security posture based on
                  the completed passive security checks.

                </p>

              </div>


              {/* =================================================
                  RISK CARD
              ================================================= */}

              <div className="risk-card">

                <div className="score-label">
                  RISK LEVEL
                </div>


                <div className="modern-gauge">

                  <div className="gauge-background"></div>

                  <div className="gauge-inner"></div>


                  <div className="gauge-ticks">

                    <div className="tick tick-0"></div>

                    <div className="tick tick-25"></div>

                    <div className="tick tick-50"></div>

                    <div className="tick tick-75"></div>

                    <div className="tick tick-100"></div>

                  </div>


                  <div
                    className="gauge-needle"
                    style={{
                      transform:
                        `rotate(${
                          -90 +
                          (
                            (Number(
                              result.overall_score
                            ) || 0
                            ) / 100
                          ) *
                          180
                        }deg)`,
                    }}
                  >

                    <div className="needle"></div>

                    <div className="needle-dot"></div>

                  </div>


                  <div className="gauge-value">

                    <div className="gauge-score">

                      {result.overall_score ?? 0}

                    </div>


                    <div className="gauge-max">
                      / 100
                    </div>

                  </div>

                </div>


                <div
                  className={
                    `risk-label ${
                      (
                        result.risk_level ||
                        "critical"
                      ).toLowerCase()
                    }`
                  }
                >

                  {result.risk_level || "Unknown"}

                </div>


                <div className="gauge-scale">

                  <span>
                    Low
                  </span>

                  <span>
                    Medium
                  </span>

                  <span>
                    High
                  </span>

                  <span>
                    Critical
                  </span>

                </div>

              </div>

            </div>


            {/* =================================================
                SUMMARY
            ================================================= */}

            <div className="summary-grid">


              <div className="summary-card">

                <div className="summary-icon passed-icon">
                  ✓
                </div>

                <div>

                  <span>
                    Passed Checks
                  </span>

                  <strong>

                    {summary.passed_checks ??
                      passedChecks.length}

                  </strong>

                </div>

              </div>


              <div className="summary-card">

                <div className="summary-icon failed-icon">
                  !
                </div>

                <div>

                  <span>
                    Failed Checks
                  </span>

                  <strong>

                    {summary.failed_checks ??
                      failedChecks.length}

                  </strong>

                </div>

              </div>


              <div className="summary-card">

                <div className="summary-icon ssl-icon">
                  🔒
                </div>

                <div>

                  <span>
                    SSL/TLS
                  </span>

                  <strong>

                    {
                      summary.ssl_enabled ||
                      ssl.enabled
                        ? "Enabled"
                        : "Disabled"
                    }

                  </strong>

                </div>

              </div>


              <div className="summary-card">

                <div className="summary-icon cms-icon">
                  ◉
                </div>

                <div>

                  <span>
                    CMS
                  </span>

                  <strong>

                    {cms.detected
                      ? cms.name
                      : "Not Detected"}

                  </strong>

                </div>

              </div>

            </div>


            {/* =================================================
                FINDINGS
            ================================================= */}

            <div className="findings-section">


              {/* PASSED */}

              <div className="findings-column">

                <div className="section-header">

                  <div>

                    <span className="section-kicker">
                      SECURITY CONTROLS
                    </span>

                    <h2>
                      Passed Checks
                    </h2>

                  </div>


                  <div className="count-badge passed">

                    {passedChecks.length}

                  </div>

                </div>


                {passedChecks.length > 0 ? (

                  passedChecks.map(
                    (check, index) => (

                      <div
                        className="finding-card passed-card"
                        key={`passed-${index}`}
                      >

                        <div className="finding-status">
                          ✓
                        </div>


                        <div className="finding-content">

                          <div className="finding-title-row">

                            <h3>
                              {check.header}
                            </h3>


                            <span
                              className={
                                `severity ${
                                  (
                                    check.severity ||
                                    "low"
                                  ).toLowerCase()
                                }`
                              }
                            >

                              {check.severity}

                            </span>

                          </div>


                          <p>
                            {check.description}
                          </p>

                        </div>

                      </div>

                    )
                  )

                ) : (

                  <div className="empty-card">

                    No security controls passed.

                  </div>

                )}

              </div>


              {/* FAILED */}

              <div className="findings-column">

                <div className="section-header">

                  <div>

                    <span className="section-kicker">
                      SECURITY CONTROLS
                    </span>

                    <h2>
                      Failed Checks
                    </h2>

                  </div>


                  <div className="count-badge failed">

                    {failedChecks.length}

                  </div>

                </div>


                {failedChecks.length > 0 ? (

                  failedChecks.map(
                    (check, index) => (

                      <div
                        className="finding-card failed-card"
                        key={`failed-${index}`}
                      >

                        <div className="finding-status">
                          !
                        </div>


                        <div className="finding-content">

                          <div className="finding-title-row">

                            <h3>
                              {check.header}
                            </h3>


                            <span
                              className={
                                `severity ${
                                  (
                                    check.severity ||
                                    "low"
                                  ).toLowerCase()
                                }`
                              }
                            >

                              {check.severity}

                            </span>

                          </div>


                          <p>
                            {check.description}
                          </p>


                          {check.recommendation && (

                            <div className="recommendation">

                              <strong>
                                Recommendation
                              </strong>

                              <span>
                                {check.recommendation}
                              </span>

                            </div>

                          )}

                        </div>

                      </div>

                    )
                  )

                ) : (

                  <div className="empty-card success-empty">

                    No failed security controls detected.

                  </div>

                )}

              </div>

            </div>


            {/* =================================================
                SSL + CMS DETAILS
            ================================================= */}

            <div className="details-grid">


              {/* SSL */}

              <div className="details-card">

                <div className="details-header">

                  <div>

                    <span className="section-kicker">
                      TRANSPORT SECURITY
                    </span>

                    <h2>
                      SSL / TLS
                    </h2>

                  </div>


                  <span
                    className={
                      `detail-status ${
                        ssl.enabled &&
                        ssl.valid
                          ? "secure"
                          : "danger"
                      }`
                    }
                  >

                    {ssl.enabled &&
                    ssl.valid
                      ? "Secure"
                      : "Not Secure"}

                  </span>

                </div>


                <div className="details-list">

                  <div>

                    <span>
                      Enabled
                    </span>

                    <strong>
                      {ssl.enabled
                        ? "Yes"
                        : "No"}
                    </strong>

                  </div>


                  <div>

                    <span>
                      Valid
                    </span>

                    <strong>
                      {ssl.valid
                        ? "Yes"
                        : "No"}
                    </strong>

                  </div>


                  <div>

                    <span>
                      Issuer
                    </span>

                    <strong>
                      {ssl.issuer || "N/A"}
                    </strong>

                  </div>


                  <div>

                    <span>
                      Subject
                    </span>

                    <strong>
                      {ssl.subject || "N/A"}
                    </strong>

                  </div>


                  <div>

                    <span>
                      Expires
                    </span>

                    <strong>
                      {ssl.expires || "N/A"}
                    </strong>

                  </div>


                  <div>

                    <span>
                      Days Remaining
                    </span>

                    <strong>
                      {ssl.days_remaining ??
                        "N/A"}
                    </strong>

                  </div>

                </div>

              </div>


              {/* CMS */}

              <div className="details-card">

                <div className="details-header">

                  <div>

                    <span className="section-kicker">
                      TECHNOLOGY DETECTION
                    </span>

                    <h2>
                      CMS Detection
                    </h2>

                  </div>


                  <span
                    className={
                      `detail-status ${
                        cms.detected
                          ? "detected"
                          : "neutral"
                      }`
                    }
                  >

                    {cms.detected
                      ? "Detected"
                      : "Not Detected"}

                  </span>

                </div>


                <div className="details-list">

                  <div>

                    <span>
                      Detected
                    </span>

                    <strong>

                      {cms.detected
                        ? "Yes"
                        : "No"}

                    </strong>

                  </div>


                  <div>

                    <span>
                      CMS
                    </span>

                    <strong>

                      {cms.name || "Unknown"}

                    </strong>

                  </div>


                  <div>

                    <span>
                      Version
                    </span>

                    <strong>

                      {cms.version ||
                        "Not available"}

                    </strong>

                  </div>

                </div>

              </div>

            </div>


            {/* =================================================
                EXECUTIVE RECOMMENDATION
            ================================================= */}

            <div className="recommendation-card">

              <div className="recommendation-icon">
                💡
              </div>


              <div>

                <span className="section-kicker">
                  EXECUTIVE SUMMARY
                </span>


                <h2>
                  Security Recommendation
                </h2>


                <p>

                  {summary.recommendation ||
                    "No immediate issues detected."}

                </p>

              </div>

            </div>


            {/* =================================================
                SCAN INFORMATION
            ================================================= */}

            <div className="scan-information">

              <span>

                Scan URL: {result.url}

              </span>


              <span>

                Scan Time:{" "}

                {result.timestamp || "N/A"}

              </span>

            </div>

          </section>

        )}

      </main>


      {/* =====================================================
          FOOTER
      ===================================================== */}

      <footer>

        <p>
          VulnScan Lite
        </p>

        <span>
          Passive Web Vulnerability Scanner
        </span>

      </footer>

    </div>
  );
}

export default App;