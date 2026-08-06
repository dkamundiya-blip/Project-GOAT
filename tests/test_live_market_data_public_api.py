"""
Project GOAT v0.8 — Test Suite: Public API Export Validation for Step 7.0
"""

import pytest
import goat.marketdata as md


def test_public_api_exports():
    expected_exports = [
        # Core Enums
        "StreamConnectionStatus",
        "MarketTimeframe",
        "GapReason",
        "SafetyGateStatus",
        "DerivSymbol",
        # Core Models
        "MarketTick",
        "MarketCandle",
        "MarketStreamState",
        "MarketGap",
        "ReplaySnapshot",
        # Canonical Hashing & Identifiers
        "compute_tick_id",
        "compute_candle_id",
        "compute_stream_id",
        "compute_gap_id",
        "compute_replay_id",
        "compute_report_id",
        # Engines & Coordinators
        "LiveMarketDataEngine",
        "ProcessTickOutput",
        "MarketIngestionEngine",
        "IngestionResult",
        "MarketStreamEngine",
        "MarketValidationEngine",
        "ValidationResult",
        "MarketGapDetectionEngine",
        "MarketReplayEngine",
        "ReplayResult",
        "MarketStreamSafetyGate",
        "SafetyGateResult",
        # Storage & Persistence
        "MarketDataBuffer",
        "init_marketdata_db",
        "MarketTickRepository",
        "MarketCandleRepository",
        "MarketStreamRepository",
        "MarketGapRepository",
        "ReplaySnapshotRepository",
        "MarketReportRepository",
        # Reporting Models
        "MarketTickReport",
        "MarketCandleReport",
        "MarketStreamReport",
        "MarketGapReport",
        "ReplaySnapshotReport",
        "MarketDataExecutiveReport",
    ]

    for export_name in expected_exports:
        assert hasattr(md, export_name), f"Missing public export: {export_name}"
        assert export_name in md.__all__, f"{export_name} missing from __all__"
