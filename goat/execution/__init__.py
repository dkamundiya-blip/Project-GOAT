"""
Project GOAT v0.8 — Production & Scientific Execution Engine Package (`goat.execution`)

- Step 4.1: Scientific Research Execution Engine
- Step 7.4: Production Execution Engine
"""

# Step 4.1 Scientific Execution Imports
from goat.execution.context import ScientificExecutionContext
from goat.execution.engine import (
    VALID_EXECUTION_TRANSITIONS,
    ScientificExecutionValidationError,
    ScientificResearchExecutionEngine,
)
from goat.execution.enums import ExecutionState as ScientificExecutionState
from goat.execution.enums import ExecutionState
from goat.execution.event import ExecutionEvent, compute_event_id
from goat.execution.history import ExecutionHistory
from goat.execution.model import (
    ScientificExecutionSession,
    compute_session_fingerprint,
    compute_session_id,
)
from goat.execution.reporting import generate_execution_report
from goat.execution.reporting import ScientificExecutionReport
from goat.execution.sqlite import EXECUTION_SCHEMA_VERSION, SQLiteExecutionRepository

# Step 7.4 Production Execution Engine Imports
from goat.execution.core import (
    AuditEventType,
    ExecutionAudit,
    ExecutionDecision,
    ExecutionFailure,
    ExecutionFailureCategory,
    ExecutionIntent,
    ExecutionLifecycle,
    ExecutionRequest,
    ExecutionSummary,
    compute_execution_audit_id,
    compute_execution_decision_id,
    compute_execution_failure_id,
    compute_execution_intent_id,
    compute_execution_lifecycle_id,
    compute_execution_report_id,
    compute_execution_request_id,
    compute_execution_summary_id,
)
from goat.execution.core.enums import ExecutionState as ProductionExecutionState
from goat.execution.dispatch import ExecutionDispatchEngine
from goat.execution.idempotency import ExecutionIdempotencyEngine
from goat.execution.intents import ExecutionIntentEngine
from goat.execution.lifecycle import ExecutionLifecycleEngine
from goat.execution.persistence import (
    ExecutionAuditRepository,
    ExecutionDecisionRepository,
    ExecutionFailureRepository,
    ExecutionIntentRepository,
    ExecutionLifecycleRepository,
    ExecutionReportRepository,
    init_execution_db,
)
from goat.execution.reporting import (
    ExecutionAuditReport,
    ExecutionDecisionReport,
    ExecutionExecutiveReport,
    ExecutionFailureReport,
    ExecutionIntentReport,
    ExecutionLifecycleReport,
)
from goat.execution.validation import ExecutionValidationEngine

__all__ = [
    # Legacy Step 4.1 Scientific Execution Engine
    "EXECUTION_SCHEMA_VERSION",
    "VALID_EXECUTION_TRANSITIONS",
    "ExecutionEvent",
    "ExecutionHistory",
    "ExecutionState",
    "ScientificExecutionState",
    "ScientificExecutionContext",
    "ScientificExecutionReport",
    "ScientificExecutionSession",
    "ScientificExecutionValidationError",
    "ScientificResearchExecutionEngine",
    "SQLiteExecutionRepository",
    "compute_event_id",
    "compute_session_fingerprint",
    "compute_session_id",
    "generate_execution_report",
    # Step 7.4 Production Execution Engine Enums & IDs
    "ProductionExecutionState",
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
    # Models
    "ExecutionIntent",
    "ExecutionRequest",
    "ExecutionDecision",
    "ExecutionLifecycle",
    "ExecutionAudit",
    "ExecutionFailure",
    "ExecutionSummary",
    # Subsystem Engines
    "ExecutionIntentEngine",
    "ExecutionValidationEngine",
    "ExecutionDispatchEngine",
    "ExecutionLifecycleEngine",
    "ExecutionIdempotencyEngine",
    # Persistence
    "init_execution_db",
    "ExecutionIntentRepository",
    "ExecutionDecisionRepository",
    "ExecutionLifecycleRepository",
    "ExecutionAuditRepository",
    "ExecutionFailureRepository",
    "ExecutionReportRepository",
    # Reporting
    "ExecutionIntentReport",
    "ExecutionDecisionReport",
    "ExecutionLifecycleReport",
    "ExecutionFailureReport",
    "ExecutionAuditReport",
    "ExecutionExecutiveReport",
]
