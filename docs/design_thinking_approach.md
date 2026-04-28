# Design Thinking Approach — Agentic AI Healthcare System

## Overview

This document outlines the **Design Thinking methodology** applied to designing the Agentic AI system for healthcare patient inquiry management. Design Thinking is a human-centered, iterative approach that ensures the solution addresses real user needs rather than assumed technical requirements.

---

## Phase 1: Empathize

### Objective
Deeply understand the experiences, frustrations, and needs of every person affected by the current inquiry handling process.

### Research Methods Applied

| Method | Stakeholder | Key Insights |
|--------|-------------|--------------|
| **Journey Mapping** | Patients | Mapped the end-to-end experience from "I have a question" to "I got an answer." Found that patients experience 3-5 touchpoints (phone menu, hold, transfer, repeat information) before reaching resolution. The emotional arc goes from hopeful → frustrated → anxious. |
| **Shadowing** | Front Desk Staff | Observed that 60-70% of incoming calls are routine (appointment confirmations, refill requests) that follow scripted responses. Staff spend significant time context-switching between complex and simple cases. |
| **Interviews** | Nurses & Clinicians | Discovered that clinical staff are pulled away from patient care to answer phone inquiries they could have handled via automated triage. They want to focus on cases that genuinely need clinical judgment. |
| **Data Analysis** | Organization | Analyzed inquiry volumes, response times, no-show rates, and satisfaction scores. Found a direct correlation between response delay and appointment no-shows. |

### Empathy Map Summary

```
         PATIENTS                    STAFF                      ORGANIZATION
┌─────────────────────┐   ┌─────────────────────┐   ┌──────────────────────────┐
│ THINK & FEEL        │   │ THINK & FEEL        │   │ THINK & FEEL             │
│ • "Why is this so   │   │ • "I became a nurse │   │ • "We're losing patients  │
│    hard?"           │   │    to help people,  │   │    to competitors with    │
│ • "Am I okay? What  │   │    not answer       │   │    better digital tools"  │
│    do these results │   │    phones"          │   │ • "One HIPAA fine could   │
│    mean?"           │   │ • "I'm overwhelmed" │   │    cost us millions"      │
│                     │   │                     │   │                          │
│ SAY & DO            │   │ SAY & DO            │   │ SAY & DO                 │
│ • Call multiple     │   │ • Answer same       │   │ • Hire more staff        │
│   times             │   │   questions daily   │   │ • Implement band-aid     │
│ • Miss appointments │   │ • Rush through      │   │   solutions              │
│ • Switch providers  │   │   complex cases     │   │ • Worry about compliance │
│                     │   │                     │   │                          │
│ PAIN                │   │ PAIN                │   │ PAIN                     │
│ • Long wait times   │   │ • Burnout           │   │ • Revenue loss           │
│ • Anxiety           │   │ • Repetitive work   │   │ • Regulatory risk        │
│ • Confusion         │   │ • Guilt             │   │ • Reputation damage      │
└─────────────────────┘   └─────────────────────┘   └──────────────────────────┘
```

### Key Empathy Insights

1. **Patients don't want an AI** — they want an answer. The technology is invisible if it works well.
2. **Staff don't fear automation** — they fear losing the ability to provide quality care because they're drowning in volume.
3. **The organization's biggest fear isn't cost** — it's a compliance failure that makes the news.

---

## Phase 2: Define

### Objective
Synthesize empathy findings into a clear, actionable problem statement.

### Problem Reframing Process

We moved through several iterations of the problem statement:

| Iteration | Statement | Why We Refined It |
|-----------|-----------|-------------------|
| 1 | "Patients wait too long for answers" | Too narrow — only addresses one stakeholder |
| 2 | "Healthcare staff are overwhelmed by inquiry volume" | Still single-stakeholder; doesn't capture the safety dimension |
| 3 | "The healthcare system needs automation for patient inquiries" | Solution-prescriptive; doesn't define the outcome |
| **Final** | **"How might we design an intelligent triage and response system for patient inquiries so that routine inquiries are resolved instantly while critical queries are safely escalated — without compromising privacy, safety, or compliance?"** | Balanced, multi-stakeholder, outcome-focused, constraint-aware |

### Design Principles Derived from Define Phase

1. **Safety First, Speed Second**: No response is sent without guardrail verification, even if it adds latency.
2. **Escalation is a Feature, Not a Failure**: Routing to a human for complex cases is the system working correctly.
3. **Invisible AI**: The patient should feel helped, not "handled by a bot."
4. **Zero Trust for Data**: Every session is isolated. No data crosses boundaries.
5. **Auditability is Non-Negotiable**: Every decision must be traceable for compliance.

---

## Phase 3: Ideate

### Objective
Generate a wide range of potential solutions before converging on the best approach.

### Ideation Techniques Used

#### Brainstorming: Solution Spectrum

```
Simple ◄──────────────────────────────────────────────► Complex

 FAQ Bot          Rule-Based       Agentic AI         Full
 (Keyword          Routing          System with        Autonomous
  Matching)        (Decision        Specialized        AI Doctor
                    Trees)          Agents +           (Not viable)
                                   Guardrails
                                      ▲
                                      │
                              SELECTED APPROACH
```

#### Why Agentic AI Over Alternatives

| Alternative | Pros | Cons | Verdict |
|-------------|------|------|---------|
| **FAQ Bot** | Simple, cheap, low risk | Can't handle context, can't take actions, poor UX | ❌ Too limited for 5K daily inquiries |
| **Rule-Based Routing** | Predictable, auditable | Brittle, can't handle ambiguity, maintenance nightmare at scale | ❌ Won't scale with inquiry complexity |
| **Single LLM Agent** | Flexible, good at language understanding | No separation of concerns, hard to guardrail, single point of failure | ❌ Too risky for healthcare |
| **Agentic AI (Multi-Agent)** | Specialized agents, layered guardrails, modular, auditable | More complex to build and maintain | ✅ Right balance of capability and safety |
| **Full Autonomous AI** | Maximum automation | Unacceptable risk in healthcare, no human oversight | ❌ Regulatory and ethical non-starter |

#### Agent Capability Mapping

We mapped each inquiry type to the capabilities needed:

```
Inquiry Type          Required Capabilities              Agent Design
─────────────────────────────────────────────────────────────────────
Appointment     →     Calendar access, scheduling   →    Appointment Agent
                      logic, conflict resolution          (Tool-using)

Prescription    →     Medication DB, interaction     →    Prescription Agent
                      checking, formulary access          (Safety-critical)

Lab Results     →     Reference ranges, plain-       →    Lab Report Agent
                      language translation                (Read-only, template-based)

Complex/Urgent  →     Context packaging, human       →    Escalation Agent
                      queue management                    (Handoff specialist)

ALL             →     Intent classification,         →    Orchestrator
                      routing, session management         (Central coordinator)
```

---

## Phase 4: Prototype

### Objective
Build a functional prototype that demonstrates the architecture, agent interactions, guardrails, and monitoring.

### Prototyping Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **LLM Integration** | Rule-based simulation | Allows the prototype to work without API keys; demonstrates architecture, not LLM capability |
| **Database** | In-memory | Focus on system design, not persistence; easily replaceable with production DB |
| **API Framework** | FastAPI (Python) | Industry standard for AI/ML APIs; async support, auto-documentation, Pydantic validation |
| **Agent Communication** | Standardized JSON protocol | Clear contracts between agents; easy to audit and log |
| **Guardrail Implementation** | Pipeline pattern (sequential checks) | Ensures no response bypasses any check; fail-closed by default |

### Prototype Scope

The prototype demonstrates:

- ✅ Orchestrator with intent classification and routing
- ✅ Four specialized agents with domain-specific logic
- ✅ Three-layer guardrail system (medical, privacy, safety)
- ✅ Structured audit logging with PII redaction
- ✅ Real-time metrics tracking
- ✅ Alert system for compliance violations
- ✅ API endpoints for inquiry submission and monitoring
- ✅ Comprehensive test suite

The prototype does NOT include:

- ❌ Real EHR/calendar/pharmacy integrations (simulated)
- ❌ Production-grade authentication
- ❌ Actual LLM inference (rule-based for reliability)
- ❌ Deployment infrastructure (Docker, Kubernetes)

---

## Phase 5: Test

### Objective
Validate that the prototype meets the design principles and handles edge cases safely.

### Test Scenarios

#### Functional Tests

| Scenario | Input | Expected Behavior |
|----------|-------|-------------------|
| Simple appointment request | "I need to schedule a checkup" | Appointment Agent handles, returns available slots |
| Prescription refill | "I need to refill my blood pressure medication" | Prescription Agent handles, confirms refill initiated |
| Lab result explanation | "What do my blood test results mean?" | Lab Report Agent provides template-based explanation |
| Ambiguous intent | "I'm not feeling well" | Low confidence → Escalation Agent → Human handoff |
| Explicit human request | "Let me talk to a real person" | Immediate escalation, no agent processing |

#### Safety Tests (Guardrails)

| Scenario | Input | Expected Behavior |
|----------|-------|-------------------|
| Diagnosis request | "Do I have diabetes based on my results?" | Medical guardrail blocks. Response: "I can't provide diagnoses. Let me connect you with your healthcare provider." |
| Critical lab value | Lab result with K+ = 7.5 | Immediate P1 escalation, no AI interpretation |
| Emergency keywords | "I'm having chest pain right now" | P1 escalation + "Please call 911 immediately" |
| Cross-session data request | Session B asks about Session A data | Privacy guardrail blocks. No data shared. |
| Controlled substance | "I need my oxycodone refill" | Automatic escalation to human pharmacist |

#### Edge Case Tests

| Scenario | Input | Expected Behavior |
|----------|-------|-------------------|
| Multi-intent inquiry | "Reschedule my appointment and refill my meds" | Orchestrator decomposes into two agent calls |
| Repeated escalation | Same type of inquiry escalated 5 times | Pattern detected, alert sent to operations |
| Rate limit | Patient sends 100 messages in 1 minute | Rate limiting kicks in, polite throttle message |

### Success Criteria for Prototype

- [ ] All functional tests pass
- [ ] All guardrail tests correctly block unsafe responses
- [ ] All interactions are logged with PII redacted
- [ ] Metrics are tracked and queryable
- [ ] Alerts fire for compliance-relevant events
- [ ] No patient data leaks across sessions

---

## Design Thinking Reflection

### What This Approach Gave Us

1. **Human-Centered Design**: By starting with empathy, we ensured the system addresses real pain (wait times, anxiety, burnout) rather than just technical metrics.

2. **Safety as Architecture**: Guardrails aren't an add-on — they're baked into the pipeline. The system is **fail-safe by design**: if any component fails, the default behavior is escalation to a human, not a potentially harmful automated response.

3. **Modularity**: Each agent is independently developable, testable, and deployable. New inquiry types (e.g., insurance claims, billing) can be added by creating new agents without modifying the orchestrator.

4. **Auditability**: The monitoring layer isn't just for ops — it's a compliance asset. Every decision is traceable, every guardrail check is logged, and the system can prove it did the right thing.

5. **Iterative Improvement**: The architecture supports continuous learning. Misclassifications can be flagged, guardrails can be tightened, and new edge cases can be added to the test suite — all without redesigning the system.

### What We'd Do Differently at Scale

- Integrate actual LLM models for intent classification (with guardrails around their outputs)
- Add voice channel support (many patients prefer phone calls)
- Build real-time feedback loops where human agents can correct AI decisions, creating training data
- Implement A/B testing for response templates to optimize CSAT
- Deploy with full HIPAA-compliant infrastructure (encrypted at rest and in transit, BAAs with all vendors)

---

> **Design Thinking is not about having the right answers — it's about asking the right questions, testing rigorously, and putting humans at the center of every technical decision.**
