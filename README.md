# XEROX — Autonomous Defensive Cybersecurity Intelligence Platform

[![CI Pipeline](https://github.com/ghoshankan429-sys/xerox-cybersecurity-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/ghoshankan429-sys/xerox-cybersecurity-platform/actions/workflows/ci.yml)
[![GitHub Pages](https://github.com/ghoshankan429-sys/xerox-cybersecurity-platform/actions/workflows/deploy-pages.yml/badge.svg)](https://ghoshankan429-sys.github.io/xerox-cybersecurity-platform/)

> **"Is this suspicious, why is it suspicious, and what should I do?"**

XEROX is a production-hardened, defense-in-depth cybersecurity platform engineered to triage suspect URLs, phishing/smishing messages, and deceptive screenshot overlays through deterministic rule engines, reputation intelligence, and explainable AI dossiers.

---

## Live Deployment Architecture

```
                       ┌───────────────────────────────────────────────┐
                       │       GitHub Pages (React 18 + Vite)          │
                       │ https://ghoshankan429-sys.github.io/           │
                       │        xerox-cybersecurity-platform/          │
                       └───────────────────────┬───────────────────────┘
                                               │
                                 Dual Auth (HttpOnly Cookie +
                                  Bearer Session Fallback)
                                               │
                                               ▼
                       ┌───────────────────────────────────────────────┐
                       │          Public FastAPI API Backend           │
                       │           (Render / Railway / Docker)         │
                       └───────────────┬───────────────┬───────────────┘
                                       │               │
                        Structured DB  │               │ High-Speed Cache &
                        Persistence    │               │ Rate Limiting
                                       ▼               ▼
                       ┌──────────────────┐ ┌──────────────────┐
                       │  PostgreSQL 16   │ │     Redis 7      │
                       │ (Alembic Migr.)  │ │  (Graceful Fall) │
                       └──────────────────┘ └──────────────────┘
                                       │
                      ┌────────────────┴────────────────┐
                      ▼                                 ▼
         ┌─────────────────────────┐       ┌─────────────────────────┐
         │ Deterministic Analyzers │       │   Threat Intelligence   │
         │  - URL Security Engine  │       │   - Redis Cache TTL     │
         │  - Phishing Message Eng │       │   - VirusTotal API      │
         │  - Screenshot Vision/OCR│       │   - Private IP SSRF Blk │
         └────────────┬────────────┘       └────────────┬────────────┘
                      │                                 │
                      └────────────────┬────────────────┘
                                       │
                                       ▼
                       ┌───────────────────────────────┐
                       │     Evidence-Based AI         │
                       │   (Google Gemini / Static)    │
                       └───────────────┬───────────────┘
                                       │
                                       ▼
                       ┌───────────────────────────────┐
                       │ Comprehensive Security Dossier│
                       │  - Layman & Executive Verdict │
                       │  - Defanged IOC Indicators    │
                       │  - Actionable Remediation     │
                       └───────────────────────────────┘
```

---

## Key Capabilities (Milestones 1–8)

1. **Deterministic URL Security Engine**
   - RFC 3986 canonicalization, refanging, defanging, and SHA-256 identification.
   - Comprehensive detection: IDN homograph attacks, brand impersonation, high-risk TLDs, ephemeral cloud abuse, and excessive subdomain depth.
   - SSRF and private network access prevention across IPv4/IPv6 loopbacks and RFC 1918 blocks.
2. **Message & Phishing Analysis Engine**
   - Unicode NFKC normalization, control-character stripping, and full defanging.
   - Regex-based IOC extraction: URLs, email addresses, phone numbers, IP addresses.
   - Heuristic classification: urgency triggers, financial/gift-card lures, display-name spoofing, and credential harvesting demands.
3. **Screenshot & Visual Analysis Engine**
   - Secure byte-level magic-number validation (PNG, JPEG, WEBP), dimension checking, and path-traversal immunization.
   - Optical character recognition (OCR) and layout analysis for credential dialog lures and fake login forms.
   - Cross-correlated visual scoring with extracted URLs and brand mismatch telemetry.
4. **Analyst Feedback System (`/api/v1/feedback`)**
   - Analysts can submit accuracy judgments, classification labels, and technical notes on any scan dossier.
   - Enforces strict tenant isolation and foreign key referential integrity in PostgreSQL.
5. **Dual Authentication Model**
   - Native HttpOnly `SameSite=None; Secure` cookies for production web apps.
   - Bearer token / `X-Session-Token` fallback enabling seamless cross-domain operation from GitHub Pages static frontend to public backends.
6. **Resilient Persistence & Distributed Caching**
   - PostgreSQL 16 via async SQLAlchemy + Alembic migrations with automatic URL protocol normalization (`postgres://` / `postgresql://` -> `postgresql+asyncpg://`).
   - Redis 7 caching with automatic degraded fallback and live health probing in `/health`.

---

## Repository Structure

```
/xerox
  ├── .github/workflows/          # CI/CD pipelines (Backend test matrix, GitHub Pages)
  ├── backend/                    # FastAPI asynchronous application
  │   ├── alembic/                # Database schema migrations
  │   ├── app/
  │   │   ├── ai/                 # Gemini LLM explanation provider & fallback
  │   │   ├── analyzers/          # Deterministic heuristic engines (URL, Message, Screenshot)
  │   │   ├── api/v1/             # Versioned routers (auth, analyze, feedback, health)
  │   │   ├── cache/              # Redis distributed cache client
  │   │   ├── core/               # Settings, config validation, logging
  │   │   ├── models/             # SQLAlchemy PostgreSQL entities
  │   │   ├── schemas/            # Pydantic validation contracts
  │   │   ├── security/           # Dual authentication, password hashing, session tokens
  │   │   ├── threat_intel/       # VirusTotal adapter & threat caching
  │   │   └── main.py             # FastAPI entrypoint
  │   ├── tests/                  # 120+ Pytest automated verification tests
  │   ├── Dockerfile              # Backend container definition
  │   └── requirements.txt        # Pinned production Python dependencies
  ├── frontend/                   # React 18, Vite, TypeScript, Tailwind CSS
  │   ├── src/
  │   │   ├── components/         # Cyber-Guardian HUD, badges, dossiers, error states
  │   │   ├── features/auth/      # Dual-mode AuthContext (cookies + session token)
  │   │   ├── pages/              # Dashboard, Analyze, History, Reports, Auth
  │   │   ├── services/           # Authenticated API client layer
  │   │   └── types/              # Forensic threat contracts
  │   ├── Dockerfile              # Production multi-stage Nginx container
  │   └── nginx.conf              # SPA routing reverse proxy
  ├── docker-compose.yml          # 4-service stack (postgres, redis, backend, frontend)
  ├── .env.example                # Comprehensive configuration template
  ├── Procfile                    # Cloud web service entrypoint
  ├── railway.json                # Railway deployment manifest
  └── render.yaml                 # Render Blueprint Infrastructure-as-Code
```

---

## Quick Start Guide

### Option A: Complete 4-Service Docker Compose Stack (Recommended)

Run the complete production stack (PostgreSQL, Redis, FastAPI backend, and Vite frontend) with a single command:

```bash
# 1. Clone the repository
git clone https://github.com/ghoshankan429-sys/xerox-cybersecurity-platform.git
cd xerox-cybersecurity-platform

# 2. Copy environment template
cp .env.example .env

# 3. Launch all services
docker compose up --build
```

- **Frontend UI**: `http://localhost:3000`
- **Backend API**: `http://localhost:8000`
- **API Documentation**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`

---

### Option B: Local Development Setup

#### 1. Backend Setup
```bash
cd backend
python -m venv venv

# Windows:
.\venv\Scripts\activate
# Linux / macOS:
# source venv/bin/activate

pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

#### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

The frontend development server starts at `http://localhost:5173`.

---

## Verification & Automated Testing

### Backend Test Suite (120+ Tests)
```bash
cd backend
pytest -v
```

All tests execute against an isolated asynchronous SQLite test database and mock threat intelligence providers, verifying:
- Authentication, session invalidation, and timing-safe password verification
- Deterministic URL normalization, refanging/defanging, and SSRF prevention
- Message phishing detection and IOC extraction
- Screenshot magic-byte validation, dimensions, and path-traversal defenses
- Feedback API and tenant data isolation
- Redis health check probing and monotonic scan history sorting

### Frontend Typecheck & Build
```bash
cd frontend
npm run lint    # Runs tsc --noEmit
npm run build   # Generates production bundle in frontend/dist
```

---

## Public Cloud Deployment

### Deploying Backend to Render
1. Connect your repository to [Render](https://render.com).
2. Use the included `render.yaml` Blueprint to automatically provision:
   - FastAPI Web Service
   - PostgreSQL 16 Database
   - Redis Instance
3. Set `CORS_ORIGINS` to `["https://ghoshankan429-sys.github.io"]`.

### Deploying Backend to Railway
1. Connect your repository to [Railway](https://railway.app).
2. Railway will automatically detect `railway.json` and build `backend/Dockerfile`.
3. Add PostgreSQL and Redis services from the Railway template marketplace.

### Frontend on GitHub Pages
The frontend deploys automatically to GitHub Pages on every push to `master` via the `.github/workflows/deploy-pages.yml` workflow.

---

## Defensive Security Boundaries

XEROX is strictly a defensive cybersecurity triage platform:
- **No Active Exploitation**: Never executes untrusted binaries, scripts, or payloads.
- **SSRF Immunization**: Never makes outbound connections to private, loopback, or reserved IP ranges.
- **Tenant Isolation**: Every scan and feedback record is cryptographically bound to the authenticated user.
- **Zero Plain-Text Secrets**: Passwords hashed with bcrypt; session cookies encrypted and signed with HMAC.
- **Sanitized Filenames**: All visual screenshot artifacts are stored with cryptographically generated UUIDs outside public web trees.
