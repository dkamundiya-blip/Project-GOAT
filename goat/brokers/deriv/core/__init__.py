"""
Project GOAT v0.8 — Deriv Core Subpackage
"""

from goat.brokers.deriv.core.canonical import (
    compute_deriv_account_snapshot_id,
    compute_deriv_auth_id,
    compute_deriv_execution_id,
    compute_deriv_heartbeat_id,
    compute_deriv_order_payload_id,
    compute_deriv_report_id,
    compute_deriv_session_id,
    compute_deriv_subscription_id,
)
from goat.brokers.deriv.core.enums import DerivContractType, DerivDurationUnit, DerivStreamType
from goat.brokers.deriv.core.models import (
    DerivAccountSnapshot,
    DerivAuthentication,
    DerivExecutionResponse,
    DerivHeartbeat,
    DerivMarketSubscription,
    DerivOrderPayload,
    DerivSession,
)

__all__ = [
    # Enums
    "DerivContractType",
    "DerivDurationUnit",
    "DerivStreamType",
    # Identifiers
    "compute_deriv_session_id",
    "compute_deriv_auth_id",
    "compute_deriv_account_snapshot_id",
    "compute_deriv_subscription_id",
    "compute_deriv_order_payload_id",
    "compute_deriv_execution_id",
    "compute_deriv_heartbeat_id",
    "compute_deriv_report_id",
    # Models
    "DerivSession",
    "DerivAuthentication",
    "DerivAccountSnapshot",
    "DerivMarketSubscription",
    "DerivOrderPayload",
    "DerivExecutionResponse",
    "DerivHeartbeat",
]
