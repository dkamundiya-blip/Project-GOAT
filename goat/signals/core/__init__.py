"""
Project GOAT v0.7 — Scientific Signal Core Package
"""

from goat.signals.core.canonical import (
    compute_lifecycle_event_id,
    compute_payload_id,
    compute_readiness_id,
    compute_signal_audit_id,
    compute_signal_id,
    compute_signal_report_id,
    serialize_canonical_json,
)
from goat.signals.core.enums import (
    ExecutionStatus,
    PayloadFormat,
    SignalDirection,
    SignalLifecycleState,
)
from goat.signals.core.models import (
    ExecutionReadiness,
    SignalAuditRecord,
    SignalLifecycleEvent,
    SignalPayload,
    TradingSignal,
)

__all__ = [
    "SignalDirection",
    "SignalLifecycleState",
    "PayloadFormat",
    "ExecutionStatus",
    "TradingSignal",
    "SignalPayload",
    "SignalLifecycleEvent",
    "ExecutionReadiness",
    "SignalAuditRecord",
    "compute_signal_id",
    "compute_payload_id",
    "compute_lifecycle_event_id",
    "compute_readiness_id",
    "compute_signal_audit_id",
    "compute_signal_report_id",
    "serialize_canonical_json",
]
