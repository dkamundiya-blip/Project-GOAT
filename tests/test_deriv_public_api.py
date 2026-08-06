"""
Project GOAT v0.8 — Test Suite: Deriv Public API Exports
"""

import goat.brokers.deriv as deriv


def test_deriv_public_api_exports():
    expected_exports = [
        "DerivAdapter",
        "DerivContractType",
        "DerivDurationUnit",
        "DerivStreamType",
        "compute_deriv_session_id",
        "compute_deriv_auth_id",
        "compute_deriv_account_snapshot_id",
        "compute_deriv_subscription_id",
        "compute_deriv_order_payload_id",
        "compute_deriv_execution_id",
        "compute_deriv_heartbeat_id",
        "compute_deriv_report_id",
        "DerivSession",
        "DerivAuthentication",
        "DerivAccountSnapshot",
        "DerivMarketSubscription",
        "DerivOrderPayload",
        "DerivExecutionResponse",
        "DerivHeartbeat",
        "DerivTranslationEngine",
        "DerivAuthenticationEngine",
        "DerivSessionEngine",
        "DerivMarketDataEngine",
        "DerivAccountEngine",
        "DerivOrderEngine",
        "init_deriv_db",
        "SessionRepository",
        "AuthenticationRepository",
        "MarketSubscriptionRepository",
        "OrderRepository",
        "ExecutionRepository",
        "HeartbeatRepository",
        "ReportRepository",
        "DerivSessionReport",
        "AuthenticationReport",
        "SubscriptionReport",
        "OrderTranslationReport",
        "ExecutionTranslationReport",
        "DerivExecutiveReport",
    ]

    for export in expected_exports:
        assert hasattr(deriv, export), f"Missing public export: {export}"
        assert export in deriv.__all__, f"Export not listed in __all__: {export}"
