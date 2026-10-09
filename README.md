# SCAMLENS AI — “See the Scam Before You Click”

SCAMLENS AI is an AI-powered scam detection and threat intelligence platform that analyzes suspicious messages, emails, URLs, LinkedIn profiles, recruiters, job offers, companies, and documents. It identifies potential fraud indicators, generates a weighted risk score, explains why the content is suspicious, and recommends defensive safety measures.

---

## 🚀 Key Features

* **Direct Dashboard Access**: Zero login or signup friction. Opens directly into the Security Command Center.
* **6 Specialized Vector Scanners**:
  1. **Message & Email Scanner**: Evaluates urgent coercive language, advance fees, crypto/gift card traps, and brand impersonation.
  2. **URL Threat Scanner**: Detects brand typosquatting, high-abuse TLDs, and path phishing, protected by an RFC1918 SSRF barrier that blocks localhost/internal network probes.
  3. **LinkedIn Profile Checker**: Audits profile claims, off-platform redirection to WhatsApp/Telegram, and high-return investment hooks.
  4. **Recruiter & Job Scam Detector**: Catches advance fees for home office equipment, counterfeit cashier check schemes, and text-only interviews.
  5. **Company Checker**: Verifies corporate email and domain integrity, detects public webmail usage for enterprise business, and uncovers offshore shell indicators.
  6. **Document Scanner**: Extracts text in-memory from PDF, DOCX, TXT, and image files to inspect fake invoices, wire instructions, and credential harvesting forms.
* **Persistent MySQL Database**: All scans, child findings, and generated security audit reports are stored in `scamlens_db`.
* **Forensic Audit Reports**: Exportable and printable executive audit reports with clean print formatting (`window.print()`).
* **Visual Telemetry**: Interactive charts using Recharts for risk category distributions and scan volume metrics.

---

## 🛠️ Technology Stack

* **Frontend**: React 18, Vite, Tailwind CSS, Axios, Recharts, Lucide React
* **Backend**: Python 3.10+, FastAPI, SQLAlchemy 2.0, PyMySQL, Pydantic v2, PyPDF2, python-docx, Pillow
* **Database**: MySQL 8.0 (`scamlens_db`)
* **Detection Engine**: Deterministic Weighted Rule Engine with SSRF Safeguards

---

## 📂 Project Structure

```
SCAMLENS-AI/
├── frontend/
│   ├── public/
│   │   └── shield.svg
│   ├── src/
│   │   ├── components/
│   │   │   ├── Sidebar.jsx
│   │   │   ├── Header.jsx
│   │   │   ├── RiskScoreBadge.jsx
│   │   │   ├── RiskGauge.jsx
│   │   │   ├── FindingsList.jsx
│   │   │   ├── AnalysisResultView.jsx
│   │   │   ├── PrintableReportModal.jsx
│   │   │   └── EmptyState.jsx
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── MessageScanner.jsx
│   │   │   ├── UrlScanner.jsx
│   │   │   ├── ProfileChecker.jsx
│   │   │   ├── JobScamDetector.jsx
│   │   │   ├── CompanyChecker.jsx
│   │   │   ├── DocumentScanner.jsx
│   │   │   ├── History.jsx
│   │   │   ├── Reports.jsx
│   │   │   └── Settings.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── .env
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── routes.py
│   │   ├── detection.py
│   │   └── document_parser.py
│   ├── requirements.txt
│   └── .env
├── database/
│   └── schema.sql
├── tests/
│   ├── __init__.py
│   ├── test_detection.py
│   └── test_api.py
├── .gitignore
└── README.md
```

---

## ⚡ Step-by-Step Setup on Windows

### Step 1: Create the MySQL Database

Open MySQL Workbench or MySQL Command Line Client:

```sql
CREATE DATABASE IF NOT EXISTS scamlens_db;
```

*(Note: The database tables `scans`, `findings`, and `reports` are automatically initialized by SQLAlchemy on backend startup! Alternatively, you can run `database/schema.sql`)*.

---

### Step 2: Configure the Backend Environment

In `backend/.env`, set your MySQL root password and connection string:

```env
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/scamlens_db
FRONTEND_ORIGIN=http://localhost:5173
HOST=127.0.0.1
PORT=8000
ENVIRONMENT=development
```

*(Replace `YOUR_PASSWORD` with your MySQL root password, e.g. `12345`)*.

---

### Step 3: Install Backend Dependencies & Start Server

Open PowerShell in the `backend/` directory:

```powershell
# Create Python virtual environment (optional)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install required Python packages
python -m pip install -r requirements.txt

# Start the FastAPI server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

* Backend API Docs (Swagger UI): **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**
* Health Status Endpoint: **[http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)**

---

### Step 4: Configure & Start Frontend

Open a second terminal in the `frontend/` directory:

```powershell
# Verify frontend/.env points to the backend
# VITE_API_BASE_URL=http://127.0.0.1:8000

# Install Node dependencies
npm install

# Start Vite development server
npm run dev
```

* Web Dashboard: **[http://localhost:5173](http://localhost:5173)**

---

## 🧪 Running Automated Tests

To run the automated test suite covering all 6 detection engines, SSRF protection, document parsing, and FastAPI endpoints:

```powershell
cd SCAMLENS-AI
python -m pytest tests/
```

---

## 🛡️ Risk Classification Standard

| Risk Score | Classification | Color Badge | Meaning |
| :--- | :--- | :--- | :--- |
| **0 – 19** | **Lower Observed Risk** | 🟢 Emerald | Few or no known scam signatures detected. Always maintain personal caution. |
| **20 – 39** | **Caution** | 🟡 Yellow | Minor anomalies or unverified identities present. Verify independently. |
| **40 – 59** | **Suspicious** | 🟠 Orange | Multiple high-pressure or anomalous signals detected. Do not proceed without secondary verification. |
| **60 – 79** | **High Risk** | 🔴 Red | Strong indicators of advance fee, phishing, or identity fraud detected. |
| **80 – 100** | **Very High Risk** | 🟣 Crimson | Blatant fraud, private SSRF exploit, or non-reversible payment demand detected. |
| **N/A** | **Insufficient Evidence** | ⚪ Slate | Input text too brief or limited to perform reliable pattern evaluation. |

---

## 🔒 Security & Privacy Disclaimers

1. **No External Leakage**: Message inputs and document texts are evaluated in-memory and are never uploaded to third-party generative AI cloud providers without explicit user configuration.
2. **SSRF Guard**: URLs are filtered against IPv4 and IPv6 RFC1918 loopback and private subnets before connection inspection.
3. **No Auth / Local Shared Model**: Designed for local analyst and development workstations without account overhead. Do not expose unauthenticated instances on untrusted public networks.
