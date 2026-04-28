# Postman Testing Guide (A to Z)

This guide provides step-by-step instructions to run the system locally and test the API using Postman.

---

## A. Prerequisites

1. Install Python 3.10+.
2. (Optional) Create and activate a virtual environment.
3. Install dependencies using [requirements.txt](../requirements.txt).

---

## B. Run The API Server

1. Open a terminal in the project root.
2. Start the server:

```
C:/Users/deepa/AppData/Local/Programs/Python/Python310/python.exe -m src.app
```

3. Confirm the server is running at:

```
http://127.0.0.1:8000
```

---

## C. Postman Setup

1. Open Postman.
2. Create a new collection named "Healthcare Agentic AI System".
3. Create a new environment named "local" with the variable:

```
base_url = http://127.0.0.1:8000
```

4. Select the "local" environment before testing.

---

## D. Postman Requests And Payloads

### 1) Submit Inquiry (Appointment)

- Method: POST
- URL: {{base_url}}/api/inquiry
- Headers:
  - Content-Type: application/json
- Body (raw JSON):

```
{
  "inquiry_text": "I need to schedule an appointment for a checkup",
  "patient_id": "patient-123",
  "channel": "api"
}
```

### 2) Submit Inquiry (Prescription Refill)

- Method: POST
- URL: {{base_url}}/api/inquiry
- Headers:
  - Content-Type: application/json
- Body (raw JSON):

```
{
  "inquiry_text": "I need a refill for my lisinopril medication",
  "patient_id": "patient-456",
  "channel": "api"
}
```

### 3) Submit Inquiry (Lab Report Explanation)

- Method: POST
- URL: {{base_url}}/api/inquiry
- Headers:
  - Content-Type: application/json
- Body (raw JSON):

```
{
  "inquiry_text": "Can you explain my CBC blood test results?",
  "patient_id": "patient-789",
  "channel": "api"
}
```

### 4) Submit Inquiry (Emergency / Escalation)

- Method: POST
- URL: {{base_url}}/api/inquiry
- Headers:
  - Content-Type: application/json
- Body (raw JSON):

```
{
  "inquiry_text": "I am having chest pain and trouble breathing",
  "patient_id": "patient-911",
  "channel": "api"
}
```

### 5) Get Metrics

- Method: GET
- URL: {{base_url}}/api/metrics

### 6) Get Logs

- Method: GET
- URL: {{base_url}}/api/logs

Optional query params:
- session_id
- event_type
- limit

Example URL:

```
{{base_url}}/api/logs?limit=10
```

### 7) Get Alerts

- Method: GET
- URL: {{base_url}}/api/alerts

### 8) Health Check

- Method: GET
- URL: {{base_url}}/api/health

---

## E. Expected Results (Quick Checks)

- Appointment inquiry returns category "appointment" and was_escalated false.
- Prescription refill returns category "prescription".
- Lab report inquiry returns category "lab_result".
- Emergency inquiry returns was_escalated true and escalation_priority "P1_IMMEDIATE".
- Metrics, logs, alerts, health endpoints return status 200.

---

## F. Troubleshooting

- If you see connection errors, confirm the server is running and the base_url is correct.
- If you get 422 validation errors, check the JSON body format and required fields.
- If the server fails to start, verify Python version and dependencies in [requirements.txt](../requirements.txt).

---

## G. (Optional) Verify With API Docs

Open:

```
{{base_url}}/docs
```

Use the Swagger UI to send test requests directly from the browser.
