# 🏥 Agentic AI Healthcare System

> **Candidate Assessment** — Agentic AI System Design for Healthcare Patient Inquiry Management

An intelligent, multi-agent system designed to handle 5,000+ daily patient inquiries by routing requests to specialized agents for appointment scheduling, prescription validation, lab report explanation, and human escalation — all enforced by layered guardrails and real-time compliance monitoring.

---

## 📋 Table of Contents

- [Architecture Overview](#architecture-overview)
- [System Design](#system-design)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Running the System](#running-the-system)
- [API Documentation](#api-documentation)
- [Running Tests](#running-tests)
- [Design Decisions](#design-decisions)
- [Deliverables](#deliverables)

---

## Architecture Overview

```
                    ┌──────────────────────┐
                    │   Patient Inquiry    │
                    │  (API / Chat / Voice)│
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    ORCHESTRATOR       │
                    │  • Intent Classifier  │
                    │  • Session Manager    │
                    │  • Guardrail Gateway  │
                    └──┬─────┬─────┬────┬──┘
                       │     │     │    │
              ┌────────┘     │     │    └────────┐
              ▼              ▼     ▼             ▼
        ┌──────────┐  ┌──────────┐ ┌──────────┐ ┌──────────┐
        │Appointment│  │Prescriptn│ │Lab Report│ │Escalation│
        │  Agent   │  │  Agent   │ │  Agent   │ │  Agent   │
        └────┬─────┘  └────┬─────┘ └────┬─────┘ └────┬─────┘
             └──────────────┴────┬───────┘            │
                                 ▼                    ▼
                    ┌──────────────────────┐  ┌─────────────┐
                    │   GUARDRAIL LAYER    │  │ HUMAN AGENT │
                    │  • Medical Safety    │  └─────────────┘
                    │  • Privacy Shield    │
                    │  • Compliance Check  │
                    └──────────┬───────────┘
                               ▼
                    ┌──────────────────────┐
                    │  MONITORING LAYER    │
                    │  • Audit Logger      │
                    │  • Metrics Tracker   │
                    │  • Alert Engine      │
                    └──────────────────────┘
```

---

## System Design

### Orchestrator
The central router that classifies patient inquiry intent, manages session isolation, routes to specialized agents, and enforces that every response passes through the guardrail pipeline before reaching the patient.

### Specialized Agents

| Agent | Responsibility | Safety Rules |
|-------|---------------|--------------|
| **Appointment Agent** | Schedule, reschedule, cancel, check appointments | Cancellations require human confirmation |
| **Prescription Agent** | Refills, medication info, pharmacy queries | Controlled substances always escalate; never provides dosage changes |
| **Lab Report Agent** | Explain lab results using approved templates | Never provides diagnoses; critical values trigger immediate escalation |
| **Escalation Agent** | Human handoff with context packaging | Determines priority tier (P1-P4) based on content analysis |

### Guardrails

| Guardrail | What It Blocks | Why |
|-----------|---------------|-----|
| **Medical Safety** | Diagnoses, treatment advice, dosage changes | Only licensed providers can make clinical decisions |
| **Privacy Shield** | PII in responses, cross-session data access | HIPAA compliance — minimum necessary principle |
| **Safety Check** | Emergency keywords, critical lab values | Life-threatening situations need immediate human intervention |

### Monitoring

| Component | Function |
|-----------|----------|
| **Audit Logger** | Structured logging with PII redaction for every decision |
| **Metrics Tracker** | 6 key KPIs: FRT, FCR, guardrail compliance, CSAT, escalation appropriateness, PHI leakage |
| **Alert Engine** | Real-time alerts for critical escalations, privacy breaches, and operational anomalies |

---

## Project Structure

```
novintex/
├── README.md                          # This file
├── question.md                        # Original problem statement
├── docs/
│   ├── understanding_document.md      # Steps 1-5 comprehensive analysis
│   └── design_thinking_approach.md    # Design thinking methodology
├── src/
│   ├── app.py                         # FastAPI main application
│   ├── config.py                      # Configuration & thresholds
│   ├── orchestrator/
│   │   └── router.py                  # Central orchestrator
│   ├── agents/
│   │   ├── base_agent.py              # Abstract base agent
│   │   ├── appointment_agent.py       # Appointment scheduling
│   │   ├── prescription_agent.py      # Prescription validation
│   │   ├── lab_report_agent.py        # Lab report explanation
│   │   └── escalation_agent.py        # Human escalation
│   ├── guardrails/
│   │   ├── medical_guardrail.py       # Medical advice boundaries
│   │   ├── privacy_guardrail.py       # Data privacy / PII
│   │   └── safety_guardrail.py        # Emergency detection
│   └── monitoring/
│       ├── logger.py                  # Audit logging
│       ├── metrics.py                 # Success metrics
│       └── alerts.py                  # Alert system
├── tests/
│   ├── test_orchestrator.py           # Orchestrator tests
│   ├── test_agents.py                 # Agent tests
│   ├── test_guardrails.py            # Guardrail tests
│   └── test_monitoring.py            # Monitoring tests
├── requirements.txt
└── .env.example
```

---

## Setup & Installation

### Prerequisites
- Python 3.10+
- pip

### Install

```bash
# Clone the repository
git clone https://github.com/your-username/novintex.git
cd novintex

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configure

```bash
# Copy environment template
cp .env.example .env

# Edit .env as needed (defaults work out of the box)
```

---

## Running the System

### Start the API Server

```bash
python -m src.app
```

The server starts at `http://localhost:8000`. API docs are auto-generated at `http://localhost:8000/docs`.

### Example API Calls

**Submit a patient inquiry:**
```bash
curl -X POST http://localhost:8000/api/inquiry \
  -H "Content-Type: application/json" \
  -d '{"inquiry_text": "I need to schedule an appointment for a checkup"}'
```

**Check system metrics:**
```bash
curl http://localhost:8000/api/metrics
```

**View audit logs:**
```bash
curl http://localhost:8000/api/logs
```

**Check active alerts:**
```bash
curl http://localhost:8000/api/alerts
```

**Health check:**
```bash
curl http://localhost:8000/api/health
```

---

## API Documentation

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/inquiry` | Submit a patient inquiry for processing |
| `GET` | `/api/metrics` | Get system metrics summary |
| `GET` | `/api/logs` | Retrieve audit logs (filterable by session/event) |
| `GET` | `/api/alerts` | Get active alerts and summary |
| `GET` | `/api/health` | System health check |
| `GET` | `/docs` | Interactive Swagger API documentation |

### Inquiry Request Body

```json
{
  "inquiry_text": "I need to schedule an appointment",
  "patient_id": "optional-patient-id",
  "channel": "api"
}
```

### Inquiry Response

```json
{
  "session_id": "uuid",
  "response_text": "Agent's response to the patient",
  "category": "appointment",
  "was_escalated": false,
  "escalation_priority": null,
  "response_time_ms": 12.5,
  "guardrails_passed": true,
  "timestamp": "2026-04-28T12:00:00Z"
}
```

---

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_guardrails.py -v

# Run with coverage
pytest tests/ -v --tb=short
```

### Test Coverage

| Test Suite | What It Tests |
|------------|---------------|
| `test_orchestrator.py` | Intent classification accuracy, routing logic, emergency handling |
| `test_agents.py` | All 4 agents: correct responses, escalation triggers, edge cases |
| `test_guardrails.py` | Medical safety blocks, PII detection/redaction, session isolation, emergency detection |
| `test_monitoring.py` | Audit logging, metrics calculations, alert system |

---

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Rule-based agents** | No LLM required | Prototype works out of the box; demonstrates architecture, not LLM capability |
| **FastAPI** | Python web framework | Industry standard for AI/ML APIs; async, auto-docs, Pydantic validation |
| **Pipeline guardrails** | Sequential check pattern | Fail-closed: if any check fails, the response is blocked. No bypassing. |
| **In-memory storage** | No database required | Focuses on design; easily swappable with production DB |
| **PII redaction** | Regex-based | Simple, effective for prototype; production would use NER models |
| **Keyword classification** | No ML model | Deterministic, testable, no training data needed for assessment |

---

## Deliverables

| # | Deliverable | Location |
|---|-------------|----------|
| 1 | Understanding Document (Steps 1-5) | [`docs/understanding_document.md`](docs/understanding_document.md) |
| 2 | Design Thinking Approach | [`docs/design_thinking_approach.md`](docs/design_thinking_approach.md) |
| 3 | GitHub Repository with README | This repository |

---

## License

This project was created as part of a candidate assessment for Agentic AI System Design.
