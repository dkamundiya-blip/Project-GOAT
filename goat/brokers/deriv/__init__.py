"""
Project GOAT v0.8 — Deriv Production Adapter Package (`goat.brokers.deriv`)

Translates between Deriv WebSocket API protocols and Project GOAT's
broker-independent AbstractBrokerAdapter interface defined in Step 7.2.
Raw Deriv payloads NEVER leak outside this package boundary.
"""

from goat.brokers.deriv.accounts import DerivAccountEngine
from goat.brokers.deriv.adapter import DerivAdapter
from goat.brokers.deriv.auth import DerivAuthenticationEngine
from goat.brokers.deriv.core import (
    DerivAccountSnapshot,
    DerivAuthentication,
    DerivContractType,
    DerivDurationUnit,
    DerivExecutionResponse,
    DerivHeartbeat,
    DerivMarketSubscription,
    DerivOrderPayload,
    DerivSession,
    DerivStreamType,
    compute_deriv_account_snapshot_id,
    compute_deriv_auth_id,
    compute_deriv_execution_id,
    compute_deriv_heartbeat_id,
    compute_deriv_order_payload_id,
    compute_deriv_report_id,
    compute_deriv_session_id,
    compute_deriv_subscription_id,
)
from goat.brokers.deriv.marketdata import DerivMarketDataEngine
from goat.brokers.deriv.orders import DerivOrderEngine
from goat.brokers.deriv.persistence import (
    AuthenticationRepository,
    ExecutionRepository,
    HeartbeatRepository,
    MarketSubscriptionRepository,
    OrderRepository,
    ReportRepository,
    SessionRepository,
    init_deriv_db,
)
from goat.brokers.deriv.reporting import (
    AuthenticationReport,
    DerivExecutiveReport,
    DerivSessionReport,
    ExecutionTranslationReport,
    OrderTranslationReport,
    SubscriptionReport,
)
from goat.brokers.deriv.session import DerivSessionEngine
from goat.brokers.deriv.translation import DerivTranslationEngine

__all__ = [
    # Main Adapter
    "DerivAdapter",
    # Core Enums
    "DerivContractType",
    "DerivDurationUnit",
    "DerivStreamType",
    # Core Identifiers
    "compute_deriv_session_id",
    "compute_deriv_auth_id",
    "compute_deriv_account_snapshot_id",
    "compute_deriv_subscription_id",
    "compute_deriv_order_payload_id",
    "compute_deriv_execution_id",
    "compute_deriv_heartbeat_id",
    "compute_deriv_report_id",
    # Core Models
    "DerivSession",
    "DerivAuthentication",
    "DerivAccountSnapshot",
    "DerivMarketSubscription",
    "DerivOrderPayload",
    "DerivExecutionResponse",
    "DerivHeartbeat",
    # Engines
    "DerivTranslationEngine",
    "DerivAuthenticationEngine",
    "DerivSessionEngine",
    "DerivMarketDataEngine",
    "DerivAccountEngine",
    "DerivOrderEngine",
    # Persistence
    "init_deriv_db",
    "SessionRepository",
    "AuthenticationRepository",
    "MarketSubscriptionRepository",
    "OrderRepository",
    "ExecutionRepository",
    "HeartbeatRepository",
    "ReportRepository",
    # Reporting
    "DerivSessionReport",
    "AuthenticationReport",
    "SubscriptionReport",
    "OrderTranslationReport",
    "ExecutionTranslationReport",
    "DerivExecutiveReport",
]
