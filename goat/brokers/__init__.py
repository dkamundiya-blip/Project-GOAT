"""
Project GOAT v0.8 — Broker Abstraction Framework Package (`goat.brokers`)

Step 7.2 Broker Abstraction Framework providing a broker-independent contract
between Project GOAT's production layer and all future broker implementations.
"""

from goat.brokers.account import BrokerAccountEngine
from goat.brokers.contracts import AbstractBrokerAdapter, BrokerCapabilityRegistry
from goat.brokers.core import (
    BrokerAccount,
    BrokerConnection,
    BrokerOrderIntent,
    BrokerProfile,
    BrokerType,
    ConnectionStatus,
    OrderSide,
    OrderType,
    TimeInForce,
    compute_account_id,
    compute_broker_profile_id,
    compute_connection_id,
    compute_error_id,
    compute_order_intent_id,
    compute_report_id,
)
from goat.brokers.errors import (
    AuthenticationError,
    BrokerError,
    BrokerErrorModel,
    BrokerUnavailableError,
    ConnectionError,
    OrderValidationError,
    PermissionError,
    RateLimitError,
    ReplayError,
    TimeoutError,
)
from goat.brokers.orders import BrokerOrderIntentEngine, IntentValidationResult
from goat.brokers.persistence import (
    AccountRepository,
    BrokerReportRepository,
    BrokerRepository,
    ConnectionRepository,
    ErrorRepository,
    OrderIntentRepository,
    init_brokers_db,
)
from goat.brokers.reporting import (
    AccountReport,
    BrokerCapabilityReport,
    BrokerExecutiveReport,
    BrokerProfileReport,
    ConnectionReport,
    OrderIntentReport,
)
from goat.brokers.session import BrokerSessionEngine

__all__ = [
    # Enums
    "BrokerType",
    "ConnectionStatus",
    "OrderSide",
    "OrderType",
    "TimeInForce",
    # Core Models
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
    # Contracts & Registry
    "AbstractBrokerAdapter",
    "BrokerCapabilityRegistry",
    # Session Engine
    "BrokerSessionEngine",
    # Order Intent Engine
    "BrokerOrderIntentEngine",
    "IntentValidationResult",
    # Account Engine
    "BrokerAccountEngine",
    # Error Framework
    "BrokerErrorModel",
    "BrokerError",
    "ConnectionError",
    "AuthenticationError",
    "PermissionError",
    "RateLimitError",
    "OrderValidationError",
    "BrokerUnavailableError",
    "TimeoutError",
    "ReplayError",
    # Persistence
    "init_brokers_db",
    "BrokerRepository",
    "ConnectionRepository",
    "AccountRepository",
    "OrderIntentRepository",
    "ErrorRepository",
    "BrokerReportRepository",
    # Reporting
    "BrokerProfileReport",
    "ConnectionReport",
    "AccountReport",
    "OrderIntentReport",
    "BrokerCapabilityReport",
    "BrokerExecutiveReport",
]
