"""
Project GOAT v0.8 — Test Suite: Execution Failures & Audit Logging (Exhaustive Matrix)
"""

import pytest

from goat.execution.core.canonical import compute_execution_audit_id, compute_execution_failure_id
from goat.execution.core.enums import AuditEventType, ExecutionFailureCategory
from goat.execution.core.models import ExecutionAudit, ExecutionFailure
from goat.marketdata.core.enums import DerivSymbol

SYMBOLS = [s.value for s in DerivSymbol]
CATEGORIES = [
    ExecutionFailureCategory.VALIDATION_FAILED,
    ExecutionFailureCategory.IDEMPOTENCY_VIOLATION,
    ExecutionFailureCategory.DUPLICATE_EXECUTION,
    ExecutionFailureCategory.BROKER_UNAVAILABLE,
    ExecutionFailureCategory.SESSION_EXPIRED,
    ExecutionFailureCategory.CAPITAL_EXHAUSTED,
    ExecutionFailureCategory.RISK_VIOLATION,
    ExecutionFailureCategory.SIGNAL_EXPIRED,
    ExecutionFailureCategory.MARKET_UNAVAILABLE,
    ExecutionFailureCategory.QUALIFICATION_EXPIRED,
]
AUDIT_TYPES = [
    AuditEventType.INTENT_CREATED,
    AuditEventType.VALIDATION_PASSED,
    AuditEventType.VALIDATION_FAILED,
    AuditEventType.IDEMPOTENCY_CHECKED,
    AuditEventType.ORDER_DISPATCHED,
    AuditEventType.ORDER_ACKNOWLEDGED,
    AuditEventType.ORDER_FILLED,
    AuditEventType.ORDER_REJECTED,
    AuditEventType.EXECUTION_FAILED,
]


@pytest.mark.parametrize("symbol", SYMBOLS)
@pytest.mark.parametrize("category", CATEGORIES)
def test_execution_failure_management_matrix(symbol, category):
    intent_id = f"EXI_{symbol}_1001"
    err_code = f"ERR_{category.value}"
    fail_id, c_hash = compute_execution_failure_id(intent_id, category.value, err_code, "2026-07-31T12:00:00Z")

    failure = ExecutionFailure(
        failure_id=fail_id,
        intent_id=intent_id,
        error_code=err_code,
        category=category,
        reason=f"Execution failed on {symbol} due to {category.value}",
        timestamp="2026-07-31T12:00:00Z",
        metadata={"symbol": symbol},
        canonical_hash=c_hash,
    )
    assert failure.failure_id.startswith("EXF_")
    assert failure.intent_id == intent_id
    assert failure.category == category


@pytest.mark.parametrize("symbol", SYMBOLS)
@pytest.mark.parametrize("event_type", AUDIT_TYPES)
def test_execution_audit_trail_matrix(symbol, event_type):
    intent_id = f"EXI_{symbol}_1001"
    audit_id, c_hash = compute_execution_audit_id(intent_id, event_type.value, "2026-07-31T12:00:00Z")

    audit = ExecutionAudit(
        audit_id=audit_id,
        intent_id=intent_id,
        event_type=event_type,
        timestamp="2026-07-31T12:00:00Z",
        details=f"Audit log event {event_type.value} for {symbol}",
        metadata={"symbol": symbol},
        canonical_hash=c_hash,
    )
    assert audit.audit_id.startswith("EXA_")
    assert audit.event_type == event_type
