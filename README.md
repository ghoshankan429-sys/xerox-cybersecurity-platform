# XEROX — Standalone AI-Assisted Cybersecurity Analysis Platform

> **"Is this suspicious, why is it suspicious, and what should I do?"**

XEROX is an autonomous, standalone cybersecurity analysis platform designed to inspect suspicious URLs and social engineering lures through deterministic evidence, threat intelligence, and explainable AI summaries.

---

## Core Pipeline Architecture

```
User Input (URL / Message)
         │
         ▼
Input Normalization
         │
         ▼
Deterministic Security Engine
         │
         ▼
Redis Cache
  ├── HIT  → Cached Threat Intel
  └── MISS → Threat Intel Adapter (VirusTotal) ──> Cache in Redis with TTL
         │
         ▼
Structured Findings
         │
         ▼
AI Explanation (Google Gemini / Fallback)
         │
         ▼
Security Report & Async Audit Logging
```

---

## Monorepo Layout

```
/xerox
  /frontend              # React 18, Vite, TypeScript, Tailwind CSS
    /src
      /components        # Sentinel Robot HUD, visualizers
      /pages             # Dashboard, Analyze, History, Reports, Settings, Auth
      /layouts           # MainLayout & navigation
      /features          # auth, dashboard, analysis, history, reports, settings
      /services          # API client layer
      /hooks             # UI and telemetry hooks
      /types             # Unified type definitions
      /lib               # Utilities and styling helpers
  /backend               # Python FastAPI backend
    /app
      /api               # Versioned API routes (/api/v1)
      /core              # Settings, configuration, logging
      /models            # SQLAlchemy PostgreSQL models
      /schemas           # Pydantic request/response contracts
      /services          # Application business logic
      /security          # Auth, password hashing, JWT
      /analyzers         # Deterministic URL and Message analyzers
      /threat_intel      # Provider abstraction & VirusTotal adapter
      /ai                # LLM explanation provider abstraction
      /cache             # Redis cache client & graceful fallback
      /database          # Database engine and session lifecycle
      /workers           # Asynchronous audit log dispatchers
  /docs                  # Architecture and security specifications
  /tests                 # Monorepo and integration test suites
  /.github               # CI/CD automated workflow definitions
  .env.example           # Environment template (no secrets)
  README.md              # Project overview and runbook
```

---

## Quick Start Guide

### Prerequisites
- Python 3.11+ (tested on Python 3.14)
- Node.js 20+ (tested on Node.js 24)
- npm 10+

### 1. Configure Environment
```bash
cp .env.example .env
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate          # On Windows (or source venv/bin/activate on Linux/macOS)
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
- API Base: `http://127.0.0.1:8000`
- Swagger Docs: `http://127.0.0.1:8000/docs`
- Health Endpoint: `http://127.0.0.1:8000/api/v1/health`

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
- Frontend UI: `http://localhost:5173`

### 4. Run Automated Tests
```bash
# Run full suite from repository root:
.\backend\venv\Scripts\python.exe -m pytest tests backend/tests -v

# Frontend build & typecheck:
cd frontend && npm run build
```

---

## Defensive Security Boundaries
XEROX is strictly defensive:
- Never detonates or executes malware
- Never executes untrusted links or JavaScript
- Never stores unhashed passwords or plain-text secrets
- Scopes all user queries to the authenticated tenant
