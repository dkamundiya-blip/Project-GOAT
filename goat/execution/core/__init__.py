"""
Project GOAT v0.8 — Execution Core Subpackage
"""

from goat.execution.core.canonical import (
    compute_execution_audit_id,
    compute_execution_decision_id,
    compute_execution_failure_id,
    compute_execution_intent_id,
    compute_execution_lifecycle_id,
    compute_execution_report_id,
    compute_execution_request_id,
    compute_execution_summary_id,
)
from goat.execution.core.enums import AuditEventType, ExecutionFailureCategory, ExecutionState
from goat.execution.core.models import (
    ExecutionAudit,
    ExecutionDecision,
    ExecutionFailure,
    ExecutionIntent,
    ExecutionLifecycle,
    ExecutionRequest,
    ExecutionSummary,
)

__all__ = [
    # Enums
    "ExecutionState",
    "ExecutionFailureCategory",
    "AuditEventType",
    # Identifiers
    "compute_execution_intent_id",
    "compute_execution_request_id",
    "compute_execution_decision_id",
    "compute_execution_lifecycle_id",
    "compute_execution_audit_id",
    "compute_execution_failure_id",
    "compute_execution_summary_id",
    "compute_execution_report_id",
    # Models
    "ExecutionIntent",
    "ExecutionRequest",
    "ExecutionDecision",
    "ExecutionLifecycle",
    "ExecutionAudit",
    "ExecutionFailure",
    "ExecutionSummary",
]
