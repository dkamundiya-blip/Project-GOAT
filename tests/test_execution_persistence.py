"""
Project GOAT v0.8 — Test Suite: Production Execution Persistence (Exhaustive Matrix)
"""

import pytest

from goat.brokers.core.enums import OrderSide
from goat.execution.core.canonical import (
    compute_execution_audit_id,
    compute_execution_decision_id,
    compute_execution_failure_id,
    compute_execution_lifecycle_id,
)
from goat.execution.core.enums import AuditEventType, ExecutionFailureCategory, ExecutionState
from goat.execution.core.models import (
    ExecutionAudit,
    ExecutionDecision,
    ExecutionFailure,
    ExecutionLifecycle,
)
from goat.execution.intents.engine import ExecutionIntentEngine
from goat.execution.persistence.repository import (
    ExecutionAuditRepository,
    ExecutionDecisionRepository,
    ExecutionFailureRepository,
    ExecutionIntentRepository,
    ExecutionLifecycleRepository,
    ExecutionReportRepository,
    init_execution_db,
)
from goat.marketdata.core.enums import DerivSymbol

SYMBOLS = [s.value for s in DerivSymbol]
SIDES = [OrderSide.BUY, OrderSide.SELL]
AMOUNTS = [1.0, 5.0, 10.0, 50.0]


@pytest.fixture
def db_conn():
    conn = init_execution_db(":memory:")
    yield conn
    conn.close()


@pytest.mark.parametrize("symbol,side,amount", [(sym, s, a) for sym in SYMBOLS for s in SIDES for a in AMOUNTS])
def test_execution_intent_persistence_matrix(db_conn, symbol, side, amount):
    repo = ExecutionIntentRepository(db_conn)
    engine = ExecutionIntentEngine()

    intent = engine.create_intent(
        signal_id=f"SIG_{symbol}",
        sizing_decision_id="SIZ_1",
        allocation_id="ALL_1",
        broker_id="BRK_DERIV",
        symbol=symbol,
        side=side,
        quantity=amount,
    )

    repo.save(intent)
    fetched = repo.get_by_id(intent.intent_id)
    assert fetched is not None
    assert fetched.intent_id == intent.intent_id
    assert fetched.symbol == symbol
    assert fetched.side == side
    assert fetched.quantity == amount


@pytest.mark.parametrize("symbol", SYMBOLS)
def test_execution_decision_lifecycle_failure_persistence_matrix(db_conn, symbol):
    intent_engine = ExecutionIntentEngine()
    intent = intent_engine.create_intent(
        signal_id=f"SIG_{symbol}",
        sizing_decision_id="SIZ_1",
        allocation_id="ALL_1",
        broker_id="BRK_DERIV",
        symbol=symbol,
        side=OrderSide.BUY,
        quantity=10.0,
    )
    ExecutionIntentRepository(db_conn).save(intent)

    # Decision
    d_repo = ExecutionDecisionRepository(db_conn)
    d_id, d_hash = compute_execution_decision_id(intent.intent_id, True, "2026-07-31T12:00:00Z")
    decision = ExecutionDecision(
        decision_id=d_id,
        intent_id=intent.intent_id,
        approved=True,
        explanation="Validated",
        timestamp="2026-07-31T12:00:00Z",
        metadata={},
        canonical_hash=d_hash,
    )
    d_repo.save(decision)
    assert d_repo.get_by_id(d_id) is not None

    # Lifecycle
    l_repo = ExecutionLifecycleRepository(db_conn)
    l_id, l_hash = compute_execution_lifecycle_id(intent.intent_id, "VALIDATED", "2026-07-31T12:00:00Z")
    lc = ExecutionLifecycle(
        lifecycle_id=l_id,
        intent_id=intent.intent_id,
        state=ExecutionState.VALIDATED,
        previous_state=ExecutionState.CREATED,
        transition_timestamp="2026-07-31T12:00:00Z",
        explanation="Transition",
        metadata={},
        canonical_hash=l_hash,
    )
    l_repo.save(lc)
    assert l_repo.get_by_id(l_id) is not None

    # Audit
    a_repo = ExecutionAuditRepository(db_conn)
    a_id, a_hash = compute_execution_audit_id(intent.intent_id, "VALIDATION_PASSED", "2026-07-31T12:00:00Z")
    audit = ExecutionAudit(
        audit_id=a_id,
        intent_id=intent.intent_id,
        event_type=AuditEventType.VALIDATION_PASSED,
        timestamp="2026-07-31T12:00:00Z",
        details="Audit details",
        metadata={},
        canonical_hash=a_hash,
    )
    a_repo.save(audit)
    assert a_repo.get_by_id(a_id) is not None

    # Failure
    f_repo = ExecutionFailureRepository(db_conn)
    f_id, f_hash = compute_execution_failure_id(intent.intent_id, "VALIDATION_FAILED", "ERR_1", "2026-07-31T12:00:00Z")
    failure = ExecutionFailure(
        failure_id=f_id,
        intent_id=intent.intent_id,
        error_code="ERR_1",
        category=ExecutionFailureCategory.VALIDATION_FAILED,
        reason="Failure test",
        timestamp="2026-07-31T12:00:00Z",
        metadata={},
        canonical_hash=f_hash,
    )
    f_repo.save(failure)
    assert f_repo.get_by_id(f_id) is not None

    # Report
    r_repo = ExecutionReportRepository(db_conn)
    r_repo.save_report(f"EXM_{symbol}", "EXECUTIVE", "2026-07-31T12:00:00Z", "# Report", "{}", "HASH_1")
