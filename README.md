# VulnScan Lite

A lightweight passive web security scanner that analyzes a website's security posture and generates an easy-to-understand Security Health Report.

## Features

- URL validation and normalization
- HTTP security header analysis
- SSL/TLS certificate inspection
- CMS detection
- Security score and grade calculation
- Risk-level classification
- Executive security recommendations
- Asynchronous scan processing
- Flask REST API backend
- React-based frontend
- Celery + Redis/Memurai worker support

## Security Checks

### HTTP Security Headers

VulnScan Lite checks for important security headers including:

- Content-Security-Policy
- X-Frame-Options
- Strict-Transport-Security
- X-Content-Type-Options
- Referrer-Policy
- Permissions-Policy

Each check reports its status, severity, description, and—when applicable—a recommendation.

### SSL/TLS

The scanner checks:

- Whether HTTPS is enabled
- Certificate validity
- Certificate issuer
- Certificate subject
- Certificate expiration
- Remaining certificate validity

### CMS Detection

The scanner attempts to identify supported CMS technologies and reports the detected CMS and version when available.

## Security Scoring

The application combines the results of its passive checks into an overall score from 0 to 100.

The report includes:

- Overall score
- Letter grade
- Risk level
- Passed checks
- Failed checks
- Recommendations

## Technology Stack

### Backend

- Python
- Flask
- Celery
- Redis-compatible queue (Redis/Memurai)
- Requests

### Frontend

- React
- JavaScript
- CSS
- Vite

## Project Structure

```text
VulnScan-Lite/
├── backend/
│   ├── scanner/
│   ├── tasks/
│   ├── app.py
│   ├── celery_app.py
│   └── ...
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── ...
│
├── README.md
├── LICENSE
├── SECURITY.md
├── CONTRIBUTING.md
└── .gitignore
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/sourav2442/VulnScan-Lite.git
cd VulnScan-Lite
```

### 2. Backend setup

On Windows PowerShell:

```powershell
cd backend
python -m venv venv
.env\Scripts\Activate.ps1
pip install -r requirements.txt
```

If your environment uses a different dependency file, install the packages listed by the project.

### 3. Redis-compatible service

The asynchronous worker requires a Redis-compatible service.

On Windows, the development setup used by this project can use Memurai.

Make sure the service is running before starting the worker.

### 4. Start the Celery worker

From the `backend` directory:

```powershell
celery -A celery_app worker --loglevel=info
```

### 5. Start Flask

In another terminal:

```powershell
cd backend
.env\Scripts\Activate.ps1
python app.py
```

The backend runs at:

```text
http://127.0.0.1:5001
```

### 6. Start the frontend

In another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the URL provided by Vite, usually:

```text
http://localhost:5173
```

## Example Workflow

1. Enter a website URL.
2. Start a scan.
3. The backend creates a scan job.
4. The worker processes the passive checks.
5. The frontend polls the scan status.
6. The completed Security Health Report is displayed.

## Example Report

A successful report can contain information similar to:

```text
Overall Score: 87/100
Grade: A
Risk Level: Medium

Passed Checks: 5
Failed Checks: 1

SSL/TLS: Enabled
CMS: Not Detected
```

Results vary depending on the target website and its current configuration.

## Scope and Responsible Use

VulnScan Lite is designed for **passive security assessment** and educational/project use.

Only scan websites and systems that you own or have explicit authorization to assess.

The project is not intended to perform destructive testing, exploitation, credential attacks, or unauthorized access.

## Limitations

- Results depend on the target website's current configuration.
- CMS detection is heuristic and may not identify every technology.
- Header presence does not guarantee that a header is configured securely.
- SSL/TLS results are based on the certificate and connection information available to the scanner.
- This tool should not be treated as a replacement for a professional security assessment.

## Development Status

VulnScan Lite is an educational cybersecurity project focused on passive web security analysis.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Author

**Sourav**

GitHub: https://github.com/sourav2442

## Future Improvements

- **Gauge Interface:** The current security score gauge is an initial implementation. A more appropriate, accurate, and visually refined gauge interface will be implemented in a future update of VulnScan Lite.
- Expand vulnerability checks and security header coverage.
- Improve CMS and technology detection.
- Add more detailed reporting and export options.
- Improve scan performance and background job handling.
- Enhance the user interface and overall dashboard experience.

