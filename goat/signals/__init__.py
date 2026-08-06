"""
Project GOAT v0.7 — Scientific Signal Generation & Delivery Package

Public API Exports for Step 6.6 & Version 0.7 Milestone.
"""

from goat.signals.core import (
    ExecutionReadiness,
    ExecutionStatus,
    PayloadFormat,
    SignalAuditRecord,
    SignalDirection,
    SignalLifecycleEvent,
    SignalLifecycleState,
    SignalPayload,
    TradingSignal,
    compute_lifecycle_event_id,
    compute_payload_id,
    compute_readiness_id,
    compute_signal_audit_id,
    compute_signal_id,
    compute_signal_report_id,
    serialize_canonical_json,
)
from goat.signals.delivery import SignalDeliveryEngine
from goat.signals.engine import ScientificSignalEngineCoordinator
from goat.signals.generation import (
    ExecutionReadinessEngine,
    ScientificSignalGenerationEngine,
)
from goat.signals.lifecycle import SignalLifecycleEngine
from goat.signals.payloads import SignalPayloadGenerator
from goat.signals.persistence import (
    ExecutionReadinessRepository,
    SignalAuditRepository,
    SignalLifecycleRepository,
    SignalPayloadRepository,
    SignalReportRepository,
    TradingSignalRepository,
    init_signals_db,
)
from goat.signals.reporting import (
    ExecutionReadinessReport,
    SignalAuditReport,
    SignalExecutiveReport,
    SignalLifecycleReport,
    SignalPayloadReport,
    TradingSignalReport,
)

__all__ = [
    # Core Models & Enums
    "SignalDirection",
    "SignalLifecycleState",
    "PayloadFormat",
    "ExecutionStatus",
    "TradingSignal",
    "SignalPayload",
    "SignalLifecycleEvent",
    "ExecutionReadiness",
    "SignalAuditRecord",
    # Identifiers & Canonical Hashing
    "compute_signal_id",
    "compute_payload_id",
    "compute_lifecycle_event_id",
    "compute_readiness_id",
    "compute_signal_audit_id",
    "compute_signal_report_id",
    "serialize_canonical_json",
    # Engines & Coordinators
    "ScientificSignalEngineCoordinator",
    "ScientificSignalGenerationEngine",
    "ExecutionReadinessEngine",
    "SignalLifecycleEngine",
    "SignalDeliveryEngine",
    "SignalPayloadGenerator",
    # Reports
    "TradingSignalReport",
    "SignalPayloadReport",
    "SignalLifecycleReport",
    "ExecutionReadinessReport",
    "SignalAuditReport",
    "SignalExecutiveReport",
    # Repositories & Database Initialization
    "init_signals_db",
    "TradingSignalRepository",
    "SignalPayloadRepository",
    "SignalLifecycleRepository",
    "ExecutionReadinessRepository",
    "SignalAuditRepository",
    "SignalReportRepository",
]
