# XEROX — Architecture & System Specification

## 1. Product Mission
**XEROX** is a standalone, AI-assisted cybersecurity analysis platform engineered to answer three core questions when inspecting suspicious digital content:
1. **Is this suspicious?** (Verdict & Explainable Risk Assessment)
2. **Why is it suspicious?** (Evidence-backed technical telemetry & heuristics)
3. **What should I do?** (Actionable, prioritized defensive guidance)

> **Important Boundary**: XEROX is strictly standalone and completely separate from any personal AI assistant. XEROX operates exclusively in a defensive inspection role and **never executes** malicious payloads, detonates malware, harvests credentials, or acts as a sandbox.

---

## 2. Core Inspection Pipeline

```
User Input (URL / Message)
         │
         ▼
┌─────────────────────────────────────────┐
│        Input Normalization Layer        │
│  - Type detection, defanging, hashing   │
│  - Extracts indicators (domains, IPs)   │
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│        Deterministic Security Engine    │
│  - Shannon entropy & typosquatting      │
│  - Suspicious TLD & deceptive domains   │
│  - Social engineering & urgency lures   │
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│            Redis Cache Layer            │
│  - Checks indicator hash / normalized ID│
└───────────┬─────────────────┬───────────┘
            │ HIT             │ MISS
            ▼                 ▼
   ┌────────────────┐   ┌─────────────────────────────┐
   │ Cached Intel   │   │ Threat Intelligence Adapter │
   │ (Fast Return)  │   │  - VirusTotal lookup        │
   │                │   │  - TTL caching to Redis     │
   │                │   │  - Graceful fallback        │
   └────────┬───────┘   └──────────────┬──────────────┘
            │                          │
            └───────────┬──────────────┘
                        │
                        ▼
┌─────────────────────────────────────────┐
│           Structured Findings           │
│  - Categorized indicators & severities  │
│  - Explainable composite risk score     │
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│            AI Synthesis Layer           │
│  - Translates evidence into clarity     │
│  - Executive summary & lay verdict      │
│  - Defensive recommended actions        │
│  - Explicit uncertainty statement       │
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│          Final Security Report          │
│  - Persisted to DB (user-scoped)        │
│  - Async audit log dispatched           │
└─────────────────────────────────────────┘
```

---

## 3. Data Integrity & Isolation
- All scan records, findings, and audit logs are strictly partitioned by authenticated `user_id`.
- Users cannot enumerate, view, or modify scans belonging to other accounts.
- Sensitive credentials, auth tokens, and raw secrets are never logged or stored in plain text.

---

## 4. Cache-First Threat Intelligence & Resiliency
- Threat intelligence queries check Redis first.
- If VirusTotal is unconfigured, rate-limited, or unavailable, the Security Engine gracefully completes using deterministic heuristics without halting the analysis pipeline.
