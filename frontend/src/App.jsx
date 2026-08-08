import { useState } from "react";
import GaugeComponent from "react-gauge-component";
import "./App.css";

function App() {
  const [url, setUrl] = useState("");
  const [scanId, setScanId] = useState(null);
  const [status, setStatus] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const startScan = async () => {
    if (!url.trim()) {
      setError("Please enter a website URL.");
      return;
    }

    setError("");
    setResult(null);
    setScanId(null);
    setStatus("Submitting scan...");

    try {
      const response = await fetch("http://127.0.0.1:5001/scan", {
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

      pollScanStatus(data.scan_id);
    } catch (err) {
      setStatus("");
      setError(err.message);
    }
  };

  const pollScanStatus = async (id) => {
    try {
      const response = await fetch(
        `http://127.0.0.1:5001/scan/${id}/status`
      );

      const data = await response.json();

      if (!response.ok || !data.success) {
        throw new Error(data.error || "Unable to check scan status.");
      }

      const currentStatus = data.status;

      if (
        currentStatus === "queued" ||
        currentStatus === "started" ||
        currentStatus === "deferred"
      ) {
        setStatus(
          currentStatus === "queued"
            ? "Scan queued..."
            : "Scan in progress..."
        );

        setTimeout(() => {
          pollScanStatus(id);
        }, 2000);

        return;
      }

      if (currentStatus === "finished") {
        setStatus("Scan completed.");
        setResult(data.result);
        return;
      }

      if (currentStatus === "failed") {
        setStatus("");
        setError(data.error || "The scan failed.");
        return;
      }

      setStatus(`Scan status: ${currentStatus}`);

      setTimeout(() => {
        pollScanStatus(id);
      }, 2000);
    } catch (err) {
      setStatus("");
      setError(err.message);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <div className="logo">VulnScan Lite</div>
        <div className="subtitle">
          On-Demand Web Vulnerability Scanner
        </div>
      </header>

      <main className="container">
        <div className="disclaimer">
          <strong>⚠ Safety Notice</strong>
          <p>
            Only scan websites you own. This tool performs passive security
            analysis only and does not perform aggressive attacks.
          </p>
        </div>

        <section className="scanner-card">
          <h1>Website Security Scanner</h1>

          <p className="description">
            Enter a website URL to analyze its security configuration.
          </p>

          <label htmlFor="url">Website URL</label>

          <div className="scan-form">
            <input
              id="url"
              type="url"
              placeholder="https://example.com"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              disabled={status === "Submitting scan..."}
            />

            <button
              onClick={startScan}
              disabled={
                status === "Submitting scan..." ||
                status === "Scan queued..." ||
                status === "Scan in progress..."
              }
            >
              {status === "Submitting scan..." ||
              status === "Scan queued..." ||
              status === "Scan in progress..."
                ? "Scanning..."
                : "Start Scan"}
            </button>
          </div>

          {scanId && (
            <div className="scan-id">
              Scan ID: <code>{scanId}</code>
            </div>
          )}

          {status && <div className="status">{status}</div>}

          {error && <div className="error">{error}</div>}
        </section>

        {result && (
          <section className="results">
            <h2>Security Report</h2>

            <div className="score-card">
              <h3>Security Score</h3>

             <GaugeComponent
  type="semicircle"
  minValue={0}
  maxValue={100}
  value={result.overall_score}
  arc={{
    width: 0.25,
    padding: 0.02,
    cornerRadius: 3,
    subArcs: [
      {
        limit: 60,
        color: "#ef4444",
        showTick: true,
      },
      {
        limit: 70,
        color: "#f97316",
        showTick: true,
      },
      {
        limit: 80,
        color: "#eab308",
        showTick: true,
      },
      {
        limit: 100,
        color: "#22c55e",
        showTick: true,
      },
    ],
  }}
  pointer={{
    type: "arrow",
    color: "#111827",
    baseColor: "#111827",
    length: 0.75,
    width: 15,
  }}
  labels={{
    valueLabel: {
      formatTextValue: (value) => `${value}/100`,
      style: {
        fontSize: "28px",
        fontWeight: "700",
        fill: "#111827",
      },
    },
    tickLabels: {
      type: "outer",
      ticks: [
        { value: 0 },
        { value: 25 },
        { value: 50 },
        { value: 75 },
        { value: 100 },
      ],
    },
  }}
/>

              <div class Name="grade">
                Grade: <strong>{result.grade}</strong>
              </div>

              <div className="risk">
                Risk Level: <strong>{result.risk_level}</strong>
              </div>  
            </div>

            <div className="summary-grid">
              <div className="summary-card">
                <span>Passed Checks</span>
                <strong>{result.summary.passed_checks}</strong>
              </div>

              <div className="summary-card">
                <span>Failed Checks</span>
                <strong>{result.summary.failed_checks}</strong>
              </div>

              <div className="summary-card">
                <span>SSL/TLS</span>
                <strong>
                  {result.summary.ssl_enabled ? "Enabled" : "Disabled"}
                </strong>
              </div>

              <div className="summary-card">
                <span>CMS</span>
                <strong>
                  {result.summary.cms_detected
                    ? result.cms.name
                    : "Not Detected"}
                </strong>
              </div>
            </div>

            <div className="report-section">
              <h3>Passed Security Checks</h3>

              {result.headers.passed_checks.length === 0 ? (
                <p>No passed checks.</p>
              ) : (
                <div className="checks">
                  {result.headers.passed_checks.map((check) => (
                    <div className="check passed" key={check.header}>
                      <div>
                        <strong>✓ {check.header}</strong>
                        <p>{check.description}</p>
                      </div>

                      <span>{check.severity}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="report-section">
              <h3>Failed Security Checks</h3>

              {result.headers.failed_checks.length === 0 ? (
                <p>No failed checks. Excellent!</p>
              ) : (
                <div className="checks">
                  {result.headers.failed_checks.map((check) => (
                    <div className="check failed" key={check.header}>
                      <div>
                        <strong>✕ {check.header}</strong>
                        <p>{check.description}</p>

                        <div className="recommendation">
                          <strong>How to Fix:</strong>
                          <br />
                          {check.recommendation}
                        </div>
                      </div>

                      <span>{check.severity}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="report-section">
              <h3>SSL/TLS Information</h3>

              <div className="ssl-info">
                <p>
                  <strong>Status:</strong>{" "}
                  {result.ssl.enabled ? "Enabled" : "Disabled"}
                </p>

                {result.ssl.enabled && (
                  <>
                    <p>
                      <strong>Certificate:</strong>{" "}
                      {result.ssl.valid ? "Valid" : "Invalid"}
                    </p>

                    <p>
                      <strong>Issuer:</strong> {result.ssl.issuer}
                    </p>

                    <p>
                      <strong>Subject:</strong> {result.ssl.subject}
                    </p>

                    <p>
                      <strong>Expires:</strong> {result.ssl.expires}
                    </p>

                    <p>
                      <strong>Days Remaining:</strong>{" "}
                      {result.ssl.days_remaining}
                    </p>
                  </>
                )}
              </div>
            </div>

            <div className="report-section">
              <h3>CMS Detection</h3>

              <p>
                <strong>Detected:</strong>{" "}
                {result.cms.detected ? "Yes" : "No"}
              </p>

              <p>
                <strong>Platform:</strong> {result.cms.name}
              </p>

              {result.cms.version && (
                <p>
                  <strong>Version:</strong> {result.cms.version}
                </p>
              )}
            </div>

            <div className="recommendation-box">
              <strong>Overall Recommendation</strong>
              <p>{result.summary.recommendation}</p>
            </div>
          </section>
        )}
      </main>

      <footer>
        VulnScan Lite • Passive Web Security Analysis
      </footer>
    </div>
  );
}

export default App;