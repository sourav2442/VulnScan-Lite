import { useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:5001";

function App() {
  const [url, setUrl] = useState("");
  const [scanId, setScanId] = useState(null);
  const [result, setResult] = useState(null);
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const startScan = async () => {
    if (!url.trim()) {
      setError("Please enter a website URL.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);
    setScanId(null);
    setStatus("Starting scan...");

    try {
      const response = await fetch(`${API_URL}/scan`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          url: url.trim(),
        }),
      });

      const data = await response.json();

      if (!response.ok || !data.success) {
        throw new Error(data.error || "Failed to start scan.");
      }

      setScanId(data.scan_id);
      setStatus("Scan queued...");

      checkScanStatus(data.scan_id);
    } catch (err) {
      console.error("Scan error:", err);

      if (err instanceof TypeError && err.message === "Failed to fetch") {
        setError(
          "Unable to connect to VulnScan Lite backend. Please make sure the scanner server is running."
        );
      } else {
        setError(
          err.message || "Unable to start the security scan."
        );
      }

      setStatus("");
    }
  };

  const checkScanStatus = async (id) => {
    try {
      const response = await fetch(
        `${API_URL}/scan/${id}/status`
      );

      const data = await response.json();

      if (!response.ok || data.success === false) {
        throw new Error(
          data.error || "Unable to check scan status."
        );
      }

      if (data.status === "queued") {
        setLoading(true);
        setStatus("Scan queued...");
        setTimeout(() => checkScanStatus(id), 2000);
        return;
      }

      if (data.status === "started") {
        setLoading(true);
        setStatus("Scanning website...");
        setTimeout(() => checkScanStatus(id), 2000);
        return;
      }

      if (data.status === "finished") {
        setLoading(false);
        setResult(data.result);
        setStatus("Scan completed successfully.");
        return;
      }

      if (data.status === "failed") {
        setLoading(false);
        setError(data.error || "Scan failed.");
        setStatus("");
        return;
      }

      setLoading(true);
      setStatus(`Scan status: ${data.status}`);
      setTimeout(() => checkScanStatus(id), 2000);

    } catch (err) {
      console.error("Status check error:", err);

      setLoading(false);

      if (
        err instanceof TypeError &&
        err.message === "Failed to fetch"
      ) {
        setError(
          "Lost connection to the VulnScan Lite backend. Please make sure the scanner server is running."
        );
      } else {
        setError(
          err.message || "Unable to check scan status."
        );
      }

      setStatus("");
    }
  };
  const getRiskClass = (riskLevel) => {
    if (!riskLevel) {
      return "medium";
    }

    const risk = String(riskLevel).toLowerCase();

    if (risk.includes("low")) {
      return "low";
    }

    if (risk.includes("critical")) {
      return "critical";
    }

    if (risk.includes("high")) {
      return "high";
    }

    return "medium";
  };

  const getGaugeRotation = (score) => {
    const safeScore = Math.max(
      0,
      Math.min(100, Number(score) || 0)
    );

    /*
      0   = -90 degrees
      50  = 0 degrees
      100 = 90 degrees
    */

    return -90 + safeScore * 1.8;
  };

  const resetScan = () => {
    setUrl("");
    setScanId(null);
    setResult(null);
    setStatus("");
    setError("");
    setLoading(false);
  };

  const passedChecks =
    result?.headers?.passed_checks || [];

  const failedChecks =
    result?.headers?.failed_checks || [];

  const summary = result?.summary || {};

  const ssl = result?.ssl || {};

  const cms = result?.cms || {};

  return (
    <div className="app">

      {/* =========================
          HEADER
      ========================= */}

      <header className="topbar">

        <div className="brand">

          <div className="brand-icon">
            V
          </div>

          <div className="brand-text">
            <h1>VulnScan Lite</h1>
            <p>Web Security Scanner</p>
          </div>

        </div>

        <div className="status-indicator">

          <span className="status-dot"></span>

          Scanner Online

        </div>

      </header>


      {/* =========================
          MAIN
      ========================= */}

      <main className="container">

        {/* =========================
            HERO / SCAN PAGE
        ========================= */}

        {!result && (
          <section className="hero-section">

            <div className="hero-content">

              <span className="hero-badge">
                PASSIVE SECURITY ANALYSIS
              </span>

              <h2>
                Scan your website's
                <span> security posture.</span>
              </h2>

              <p className="hero-description">
                Enter a website URL to analyze security
                headers, SSL/TLS configuration, CMS
                information and overall security risk.
              </p>


              <div className="scan-form">

                <input
                  type="url"
                  placeholder="https://example.com"
                  value={url}
                  onChange={(event) =>
                    setUrl(event.target.value)
                  }
                  onKeyDown={(event) => {
                    if (event.key === "Enter") {
                      startScan();
                    }
                  }}
                />

                <button
                  onClick={startScan}
                  disabled={loading}
                >
                  {loading
                    ? "Scanning..."
                    : "Scan Website"}
                </button>

              </div>


              {status && (
                <div className="scan-status">
                  <span className="loading-dot"></span>
                  {status}
                </div>
              )}


              {error && (
                <div className="error-message">
                  {error}
                </div>
              )}

            </div>

          </section>
        )}


        {/* =========================
            RESULTS
        ========================= */}

        {result && (
          <section className="results-section">

            {/* =====================
                RESULTS HEADER
            ===================== */}

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


            {/* =====================
                SCORE + RISK
            ===================== */}

            <div className="score-section">

              {/* SCORE CARD */}

              <div className="score-card">

                <div className="score-label">
                  OVERALL SECURITY SCORE
                </div>

                <div className="score-number">
                  {result.overall_score ?? 0}
                  <span>/100</span>
                </div>

                <div className="grade">
                  Grade {result.grade || "N/A"}
                </div>

                <p className="score-description">
                  Overall security posture based on
                  the completed passive checks.
                </p>

              </div>


              {/* RISK GAUGE */}

              <div className="risk-card">

                <div className="score-label">
                  RISK LEVEL
                </div>


                <div className="modern-gauge">

                  {/* Colored gauge */}
                  <div className="gauge-background">

                    <div className="gauge-inner"></div>

                  </div>


                  {/* Gauge tick marks */}

                  <div className="gauge-ticks">

                    <span className="tick tick-0"></span>
                    <span className="tick tick-25"></span>
                    <span className="tick tick-50"></span>
                    <span className="tick tick-75"></span>
                    <span className="tick tick-100"></span>

                  </div>


                  {/* Needle */}

                  <div
                    className="gauge-needle"
                    style={{
                      transform: `rotate(${getGaugeRotation(
                        result.overall_score
                      )}deg)`,
                    }}
                  >

                    <div className="needle"></div>

                    <div className="needle-dot"></div>

                  </div>


                  {/* Center score */}

                  <div className="gauge-value">

                    <div className="gauge-score">
                      {result.overall_score ?? 0}
                    </div>

                    <div className="gauge-max">
                      /100
                    </div>

                  </div>

                </div>


                {/* Risk badge */}

                <div
                  className={`risk-label ${getRiskClass(
                    result.risk_level
                  )}`}
                >
                  {result.risk_level || "Unknown"}
                </div>


                {/* Scale */}

                <div className="gauge-scale">

                  <span>Low</span>

                  <span>Medium</span>

                  <span>High</span>

                  <span>Critical</span>

                </div>

              </div>

            </div>


            {/* =====================
                SUMMARY CARDS
            ===================== */}

            <div className="summary-grid">

              <div className="summary-card">

                <div className="summary-icon passed-icon">
                  ✓
                </div>

                <div>
                  <span>Passed Checks</span>

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
                  <span>Failed Checks</span>

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
                  <span>SSL/TLS</span>

                  <strong>
                    {summary.ssl_enabled
                      ? "Enabled"
                      : ssl.enabled
                        ? "Enabled"
                        : "Disabled"}
                  </strong>
                </div>

              </div>


              <div className="summary-card">

                <div className="summary-icon cms-icon">
                  ◉
                </div>

                <div>
                  <span>CMS</span>

                  <strong>
                    {summary.cms_detected || cms.detected
                      ? cms.name || "Detected"
                      : "Not Detected"}
                  </strong>
                </div>

              </div>

            </div>


            {/* =====================
                SECURITY FINDINGS
            ===================== */}

            <div className="findings-section">


              {/* PASSED */}

              <div className="findings-column">

                <div className="section-header">

                  <div>
                    <span className="section-kicker">
                      SECURITY ANALYSIS
                    </span>

                    <h2>
                      Passed Security Checks
                    </h2>
                  </div>

                  <span className="count-badge passed">
                    {passedChecks.length}
                  </span>

                </div>


                {passedChecks.length === 0 && (
                  <div className="empty-card">
                    No passed checks were reported.
                  </div>
                )}


                {passedChecks.map(
                  (check, index) => (

                    <div
                      className="finding-card passed-card"
                      key={index}
                    >

                      <div className="finding-status">
                        ✓
                      </div>

                      <div className="finding-content">

                        <div className="finding-title-row">

                          <h3>
                            {check.header ||
                              check.name ||
                              "Security Check"}
                          </h3>

                          {check.severity && (
                            <span
                              className={`severity ${String(
                                check.severity
                              ).toLowerCase()}`}
                            >
                              {check.severity}
                            </span>
                          )}

                        </div>

                        <p>
                          {check.description ||
                            "Security check passed successfully."}
                        </p>

                      </div>

                    </div>

                  )
                )}

              </div>


              {/* FAILED */}

              <div className="findings-column">

                <div className="section-header">

                  <div>
                    <span className="section-kicker">
                      SECURITY ANALYSIS
                    </span>

                    <h2>
                      Failed Security Checks
                    </h2>
                  </div>

                  <span className="count-badge failed">
                    {failedChecks.length}
                  </span>

                </div>


                {failedChecks.length === 0 && (
                  <div className="empty-card success-empty">
                    No failed security checks found.
                  </div>
                )}


                {failedChecks.map(
                  (check, index) => (

                    <div
                      className="finding-card failed-card"
                      key={index}
                    >

                      <div className="finding-status">
                        !
                      </div>

                      <div className="finding-content">

                        <div className="finding-title-row">

                          <h3>
                            {check.header ||
                              check.name ||
                              "Security Check"}
                          </h3>

                          {check.severity && (
                            <span
                              className={`severity ${String(
                                check.severity
                              ).toLowerCase()}`}
                            >
                              {check.severity}
                            </span>
                          )}

                        </div>

                        <p>
                          {check.description ||
                            "This security check failed."}
                        </p>


                        {check.recommendation && (
                          <div className="recommendation">

                            <strong>
                              Recommendation:
                            </strong>

                            <span>
                              {check.recommendation}
                            </span>

                          </div>
                        )}

                      </div>

                    </div>

                  )
                )}

              </div>

            </div>


            {/* =====================
                SSL + CMS
            ===================== */}

            <div className="details-grid">


              {/* SSL */}

              <div className="details-card">

                <div className="details-header">

                  <div>
                    <span className="section-kicker">
                      CERTIFICATE
                    </span>

                    <h2>
                      SSL/TLS Certificate
                    </h2>
                  </div>

                  <span
                    className={
                      ssl.enabled && ssl.valid
                        ? "detail-status secure"
                        : "detail-status danger"
                    }
                  >
                    {ssl.enabled && ssl.valid
                      ? "Valid"
                      : "Issue"}
                  </span>

                </div>


                <div className="details-list">

                  <div>
                    <span>Status</span>

                    <strong>
                      {ssl.enabled
                        ? "Enabled"
                        : "Disabled"}
                    </strong>
                  </div>


                  <div>
                    <span>Issuer</span>

                    <strong>
                      {ssl.issuer || "Unknown"}
                    </strong>
                  </div>


                  <div>
                    <span>Subject</span>

                    <strong>
                      {ssl.subject || "Unknown"}
                    </strong>
                  </div>


                  <div>
                    <span>Expires</span>

                    <strong>
                      {ssl.expires || "Unknown"}
                    </strong>
                  </div>


                  <div>
                    <span>Days Remaining</span>

                    <strong>
                      {ssl.days_remaining ?? "N/A"}
                    </strong>
                  </div>

                </div>

              </div>


              {/* CMS */}

              <div className="details-card">

                <div className="details-header">

                  <div>
                    <span className="section-kicker">
                      TECHNOLOGY
                    </span>

                    <h2>
                      CMS Detection
                    </h2>
                  </div>

                  <span
                    className={
                      cms.detected
                        ? "detail-status detected"
                        : "detail-status neutral"
                    }
                  >
                    {cms.detected
                      ? "Detected"
                      : "Not Detected"}
                  </span>

                </div>


                <div className="details-list">

                  <div>
                    <span>CMS</span>

                    <strong>
                      {cms.name || "Unknown"}
                    </strong>
                  </div>


                  <div>
                    <span>Version</span>

                    <strong>
                      {cms.version ||
                        "Not detected"}
                    </strong>
                  </div>

                </div>

              </div>

            </div>


            {/* =====================
                EXECUTIVE
                RECOMMENDATION
            ===================== */}

            <div className="recommendation-card">

              <div className="recommendation-icon">
                💡
              </div>

              <div>

                <span className="section-kicker">
                  NEXT STEPS
                </span>

                <h2>
                  Executive Recommendation
                </h2>

                <p>
                  {summary.recommendation ||
                    "Review the failed security checks and apply the recommended security controls."}
                </p>

              </div>

            </div>


            {/* =====================
                SCAN INFORMATION
            ===================== */}

            <div className="scan-information">

              <span>
                Scan ID: {scanId}
              </span>

              <span>
                ✓ Scan completed successfully
              </span>

            </div>

          </section>
        )}

      </main>


      {/* =========================
          FOOTER
      ========================= */}

      <footer>

        <p>
          VulnScan Lite — Passive Web Security Scanner
        </p>

        <span>
          Security analysis for authorized websites
        </span>

      </footer>

    </div>
  );
}

export default App;