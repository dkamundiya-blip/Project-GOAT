"""
Project GOAT v0.8 — Test Suite: Production Execution Public API Validation
"""

import goat.execution


def test_execution_public_api_exports():
    assert hasattr(goat.execution, "__all__")
    all_exports = goat.execution.__all__

    expected_symbols = [
        "ExecutionState",
        "ExecutionFailureCategory",
        "AuditEventType",
        "compute_execution_intent_id",
        "compute_execution_request_id",
        "compute_execution_decision_id",
        "compute_execution_lifecycle_id",
        "compute_execution_audit_id",
        "compute_execution_failure_id",
        "compute_execution_summary_id",
        "compute_execution_report_id",
        "ExecutionIntent",
        "ExecutionRequest",
        "ExecutionDecision",
        "ExecutionLifecycle",
        "ExecutionAudit",
        "ExecutionFailure",
        "ExecutionSummary",
        "ExecutionIntentEngine",
        "ExecutionValidationEngine",
        "ExecutionDispatchEngine",
        "ExecutionLifecycleEngine",
        "ExecutionIdempotencyEngine",
        "init_execution_db",
        "ExecutionIntentRepository",
        "ExecutionDecisionRepository",
        "ExecutionLifecycleRepository",
        "ExecutionAuditRepository",
        "ExecutionFailureRepository",
        "ExecutionReportRepository",
        "ExecutionIntentReport",
        "ExecutionDecisionReport",
        "ExecutionLifecycleReport",
        "ExecutionFailureReport",
        "ExecutionAuditReport",
        "ExecutionExecutiveReport",
    ]

    for symbol in expected_symbols:
        assert symbol in all_exports
        assert hasattr(goat.execution, symbol)
