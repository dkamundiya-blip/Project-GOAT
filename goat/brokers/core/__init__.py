"""
Project GOAT v0.8 — Broker Core Subpackage
"""

from goat.brokers.core.canonical import (
    compute_account_id,
    compute_broker_profile_id,
    compute_connection_id,
    compute_error_id,
    compute_order_intent_id,
    compute_report_id,
)
from goat.brokers.core.enums import (
    BrokerType,
    ConnectionStatus,
    OrderSide,
    OrderType,
    TimeInForce,
)
from goat.brokers.core.models import (
    BrokerAccount,
    BrokerConnection,
    BrokerOrderIntent,
    BrokerProfile,
)

__all__ = [
    # Enums
    "BrokerType",
    "ConnectionStatus",
    "OrderSide",
    "OrderType",
    "TimeInForce",
    # Models
    "BrokerProfile",
    "BrokerConnection",
    "BrokerAccount",
    "BrokerOrderIntent",
    # Identifiers
    "compute_broker_profile_id",
    "compute_connection_id",
    "compute_account_id",
    "compute_order_intent_id",
    "compute_error_id",
    "compute_report_id",
]
