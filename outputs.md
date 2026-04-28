<img width="1438" height="984" alt="Screenshot 2026-04-28 151155" src="https://github.com/user-attachments/assets/82086d5b-0c93-4bee-b3d4-2b494b4d4b6d" />
<img width="1429" height="985" alt="Screenshot 2026-04-28 151407" src="https://github.com/user-attachments/assets/e6d99da0-06ca-4c68-982d-999e28dc3fa7" />
<img width="1437" height="987" alt="Screenshot 2026-04-28 151433" src="https://github.com/user-attachments/assets/78e9d6a9-9c84-4ae9-b594-700032f09e3e" />
<img width="1421" height="978" alt="Screenshot 2026-04-28 151535" src="https://github.com/user-attachments/assets/0b52146b-b00f-4036-a92e-d78d8f799ff9" />
<img width="1415" height="987" alt="Screenshot 2026-04-28 152446" src="https://github.com/user-attachments/assets/43c931d1-ab39-4fa8-95b0-6fe4fed37eb2" />
<img width="1419" height="987" alt="Screenshot 2026-04-28 152524" src="https://github.com/user-attachments/assets/89b3018c-6e89-4792-af4e-705a9a7b7660" />
<img width="1444" height="985" alt="Screenshot 2026-04-28 152554" src="https://github.com/user-attachments/assets/1e43694c-a708-4ff1-84ac-fba5c9f51229" />
<img width="1429" height="993" alt="Screenshot 2026-04-28 153020" src="https://github.com/user-attachments/assets/f153d91a-8a71-4417-846a-d6d9b67acb60" />

pytest tests/ -v
================================================= test session starts =================================================
platform win32 -- Python 3.10.6, pytest-8.3.0, pluggy-1.6.0 -- C:\Users\deepa\OneDrive\Desktop\novintex\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\deepa\OneDrive\Desktop\back\novintix-assesment
plugins: anyio-4.13.0
collected 65 items

tests/test_agents.py::TestAppointmentAgent::test_can_handle PASSED                                               [  1%]
tests/test_agents.py::TestAppointmentAgent::test_cannot_handle_prescription PASSED                               [  3%]
tests/test_agents.py::TestAppointmentAgent::test_schedule_response PASSED                                        [  4%]
tests/test_agents.py::TestAppointmentAgent::test_cancel_triggers_escalation PASSED                               [  6%]
tests/test_agents.py::TestAppointmentAgent::test_check_appointment PASSED                                        [  7%]
tests/test_agents.py::TestPrescriptionAgent::test_can_handle PASSED                                              [  9%]
tests/test_agents.py::TestPrescriptionAgent::test_refill_known_medication PASSED                                 [ 10%]
tests/test_agents.py::TestPrescriptionAgent::test_controlled_substance_escalation PASSED                         [ 12%]
tests/test_agents.py::TestPrescriptionAgent::test_pharmacy_info PASSED                                           [ 13%]
tests/test_agents.py::TestLabReportAgent::test_can_handle PASSED                                                 [ 15%]
tests/test_agents.py::TestLabReportAgent::test_explain_cbc PASSED                                                [ 16%]
tests/test_agents.py::TestLabReportAgent::test_critical_value_escalation PASSED                                  [ 18%]
tests/test_agents.py::TestLabReportAgent::test_diagnosis_request_redirect PASSED                                 [ 20%]
tests/test_agents.py::TestEscalationAgent::test_can_handle PASSED                                                [ 21%]
tests/test_agents.py::TestEscalationAgent::test_always_escalates PASSED                                          [ 23%]
tests/test_agents.py::TestEscalationAgent::test_emergency_gets_p1 PASSED                                         [ 24%]
tests/test_guardrails.py::TestMedicalGuardrail::test_safe_response_passes PASSED                                 [ 26%]
tests/test_guardrails.py::TestMedicalGuardrail::test_diagnosis_blocked PASSED                                    [ 27%]
tests/test_guardrails.py::TestMedicalGuardrail::test_treatment_recommendation_blocked PASSED                     [ 29%]
tests/test_guardrails.py::TestMedicalGuardrail::test_dosage_change_blocked PASSED                                [ 30%]
tests/test_guardrails.py::TestMedicalGuardrail::test_safe_educational_content_passes PASSED                      [ 32%]
tests/test_guardrails.py::TestPrivacyGuardrail::test_clean_response_passes PASSED                                [ 33%]
tests/test_guardrails.py::TestPrivacyGuardrail::test_ssn_detected PASSED                                         [ 35%]
tests/test_guardrails.py::TestPrivacyGuardrail::test_pii_redaction_ssn PASSED                                    [ 36%]
tests/test_guardrails.py::TestPrivacyGuardrail::test_pii_redaction_email PASSED                                  [ 38%]
tests/test_guardrails.py::TestPrivacyGuardrail::test_pii_redaction_mrn PASSED                                    [ 40%]
tests/test_guardrails.py::TestPrivacyGuardrail::test_session_isolation PASSED                                    [ 41%]
tests/test_guardrails.py::TestPrivacyGuardrail::test_same_session_access_passes PASSED                           [ 43%]
tests/test_guardrails.py::TestSafetyGuardrail::test_normal_text_passes PASSED                                    [ 44%]
tests/test_guardrails.py::TestSafetyGuardrail::test_chest_pain_detected PASSED                                   [ 46%]
tests/test_guardrails.py::TestSafetyGuardrail::test_suicidal_ideation_detected PASSED                            [ 47%]
tests/test_guardrails.py::TestSafetyGuardrail::test_difficulty_breathing_detected PASSED                         [ 49%]
tests/test_guardrails.py::TestSafetyGuardrail::test_critical_lab_high_potassium PASSED                           [ 50%]
tests/test_guardrails.py::TestSafetyGuardrail::test_critical_lab_low_glucose PASSED                              [ 52%]
tests/test_guardrails.py::TestSafetyGuardrail::test_normal_lab_passes PASSED                                     [ 53%]
tests/test_guardrails.py::TestSafetyGuardrail::test_negative_sentiment_single_keyword PASSED                     [ 55%]
tests/test_guardrails.py::TestSafetyGuardrail::test_negative_sentiment_multiple_keywords PASSED                  [ 56%]
tests/test_monitoring.py::TestAuditLogger::test_log_inquiry PASSED                                               [ 58%]
tests/test_monitoring.py::TestAuditLogger::test_pii_redacted_in_log PASSED                                       [ 60%]
tests/test_monitoring.py::TestAuditLogger::test_log_agent_routed PASSED                                          [ 61%]
tests/test_monitoring.py::TestAuditLogger::test_log_guardrail_check PASSED                                       [ 63%]
tests/test_monitoring.py::TestAuditLogger::test_retrieve_logs_by_session PASSED                                  [ 64%]
tests/test_monitoring.py::TestMetrics::test_record_inquiry PASSED                                                [ 66%]
tests/test_monitoring.py::TestMetrics::test_response_time PASSED                                                 [ 67%]
tests/test_monitoring.py::TestMetrics::test_resolution_rate PASSED                                               [ 69%]
tests/test_monitoring.py::TestMetrics::test_guardrail_compliance PASSED                                          [ 70%]
tests/test_monitoring.py::TestMetrics::test_inquiries_by_category PASSED                                         [ 72%]
tests/test_monitoring.py::TestAlerts::test_trigger_alert PASSED                                                  [ 73%]
tests/test_monitoring.py::TestAlerts::test_get_active_alerts PASSED                                              [ 75%]
tests/test_monitoring.py::TestAlerts::test_resolve_alert PASSED                                                  [ 76%]
tests/test_monitoring.py::TestAlerts::test_alert_summary PASSED                                                  [ 78%]
tests/test_orchestrator.py::TestIntentClassification::test_appointment_intent PASSED                             [ 80%]
tests/test_orchestrator.py::TestIntentClassification::test_prescription_intent PASSED                            [ 81%]
tests/test_orchestrator.py::TestIntentClassification::test_lab_result_intent PASSED                              [ 83%]
tests/test_orchestrator.py::TestIntentClassification::test_insurance_intent PASSED                               [ 84%]
tests/test_orchestrator.py::TestIntentClassification::test_escalation_intent PASSED                              [ 86%]
tests/test_orchestrator.py::TestIntentClassification::test_unknown_intent PASSED                                 [ 87%]
tests/test_orchestrator.py::TestIntentClassification::test_low_confidence_triggers_escalation PASSED             [ 89%]
tests/test_orchestrator.py::TestInquiryRouting::test_appointment_routing PASSED                                  [ 90%]
tests/test_orchestrator.py::TestInquiryRouting::test_prescription_routing PASSED                                 [ 92%]
tests/test_orchestrator.py::TestInquiryRouting::test_lab_result_routing PASSED                                   [ 93%]
tests/test_orchestrator.py::TestInquiryRouting::test_emergency_routing PASSED                                    [ 95%]
tests/test_orchestrator.py::TestInquiryRouting::test_human_request_routing PASSED                                [ 96%]
tests/test_orchestrator.py::TestInquiryRouting::test_controlled_substance_escalation PASSED                      [ 98%]
tests/test_orchestrator.py::TestInquiryRouting::test_session_id_assigned PASSED                                  [100%]

================================================= 65 passed in 0.63s ==================================================
