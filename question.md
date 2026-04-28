CANDIDATE TASK DOCUMENT
Agentic AI System Design | Candidate Assessment
PROBLEM STATEMENT
A healthcare provider receives 5,000+ patient inquiries daily related to appointments,
prescriptions, lab results and insurance claims. Response delays are leading to missed
appointments and declining patient satisfaction. You are asked to design an Agentic AI
system where an orchestrator routes requests to specialized agents for appointment
scheduling, prescription validation, report explanation and human escalation. Guardrails
must ensure no medical advice is given beyond approved guidelines, no patient data is
shared across sessions and no critical health-related query is resolved without verification.
A monitoring layer must track every decision, escalation and potential compliance violation
in real time.
YOUR TASK
Work through each of the following steps and present your approach clearly. There is no
single correct answer — the panel is evaluating your thinking process, structure and
communication.
STEP 1 | Understand the Problem
Identify who is affected by this problem and what their real pain is. Think about every
stakeholder — the patient, the healthcare staff and the organization. What is the human cost
and what is the risk to patient safety and compliance if this problem is not solved?
STEP 2 | Define the Problem Statement
Frame the core problem in one clear, specific statement. Use the format: How Might We
[solve X] for [who] so that [outcome]? The statement must be focused enough to drive a
solution, not broad or generic.
STEP 3 | Design the Agent System
Design the Agentic AI system. Explain what the orchestrator does and how it manages the
flow. Define each specialized agent — what it handles, what tools it needs and how it
communicates. Explain how the system determines when to escalate to a human, especially
for critical or sensitive healthcare scenarios.
STEP 4 | Define the Guardrails
Identify the guardrails that must be in place. Which actions should an agent never take
without human approval? What medical, legal and data privacy constraints must be
enforced? Define thresholds, hard stops and escalation triggers. Explain why each guardrail
is critical in a healthcare context.
STEP 5 | Monitoring and Success Metrics
Explain how you would monitor this system in production. What is logged? What alerts are
triggered? How do you detect compliance violations or unsafe outputs? Define at least 4
specific success metrics.
STATUS
All five steps are completed in docs/understanding_document.md.
DELIVERABLES
Please submit:
• Understanding Document (PDF/Word)
• GitHub Repository (with README)
• Explain design thinking approach - md file
 ALL THE BEST !

---

TASK TRACKER COMPLETION (2026-04-28)

PHASE 1: DOCUMENTATION
- [x] docs/understanding_document.md — Steps 1-5 comprehensive analysis
- [x] docs/design_thinking_approach.md — Design thinking methodology

PHASE 2: BACKEND IMPLEMENTATION
- [x] src/models/schemas.py — Pydantic data models
- [x] src/config.py — Configuration
- [x] src/agents/base_agent.py — Abstract base agent
- [x] src/agents/appointment_agent.py — Appointment scheduling
- [x] src/agents/prescription_agent.py — Prescription validation
- [x] src/agents/lab_report_agent.py — Lab report explanation
- [x] src/agents/escalation_agent.py — Human escalation
- [x] src/orchestrator/router.py — Orchestrator / request router
- [x] src/guardrails/medical_guardrail.py — Medical advice boundaries
- [x] src/guardrails/privacy_guardrail.py — Data privacy / session isolation
- [x] src/guardrails/safety_guardrail.py — Critical health verification
- [x] src/monitoring/logger.py — Structured logging
- [x] src/monitoring/metrics.py — Success metrics
- [x] src/monitoring/alerts.py — Alert system
- [x] src/app.py — FastAPI application

PHASE 3: TESTS & README
- [x] tests/test_orchestrator.py
- [x] tests/test_agents.py
- [x] tests/test_guardrails.py
- [x] tests/test_monitoring.py
- [x] README.md — Project documentation
- [x] requirements.txt
- [x] .env.example

PHASE 4: VERIFICATION
- [x] Run tests (pytest): 65 passed
- [x] Verify API endpoints:
	- /, /api/health, /api/metrics, /api/logs, /api/alerts (200 OK)
	- POST /api/inquiry (200 OK, category=appointment, was_escalated=false)