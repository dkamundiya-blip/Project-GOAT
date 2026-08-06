"""
Project GOAT v0.8 — Test Suite: Public API Export Validation for Step 7.2
"""

import pytest
import goat.brokers as brk


def test_public_api_exports():
    expected_exports = [
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

    for export_name in expected_exports:
        assert hasattr(brk, export_name), f"Missing public export: {export_name}"
        assert export_name in brk.__all__, f"{export_name} missing from __all__"
