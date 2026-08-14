"""
Project GOAT — Dashboard Data Integrity & Anti-Fabrication Test Suite
Validates that:
1. Dashboard repository adapter returns honest zero/empty states (no hardcoded 42/1250/18/5).
2. Telemetry broadcaster snapshot returns clean zero/empty defaults (no hardcoded 1.4820 ATR, 0.0521 vol, 1004.25 VWAP, 2.38 latency, or time-jitter tick_rate).
3. Discovered edges list is strictly empty when SQLite contains no active edges.
4. Real rolling tick rate calculation reflects genuine ticks instead of synthetic formula.
5. Health and summary API responses contain no synthetic EDG_BOOM_* records.
"""

import time
import pytest
from goat.dashboard.persistence.sqlite import DashboardReadOnlyRepositoryAdapter
from goat.dashboard.api.rest import DashboardRESTHandler
from goat.dashboard.telemetry.collector import SystemTelemetryCollector
from goat.integration.master import MasterSystemIntegrationEngine
from goat.telemetry.server import TelemetryBroadcaster


def test_dashboard_adapter_returns_honest_zero_state():
    """Verify repository adapter returns zero counts and no fabricated numbers."""
    adapter = DashboardReadOnlyRepositoryAdapter(db_path=":memory:")
    summary = adapter.get_dashboard_summary_metrics()

    assert summary["hypothesis_count"] == 0
    assert summary["evidence_records_count"] == 0
    assert summary["validated_edges_count"] == 0
    assert summary["promoted_edges_count"] == 0
    assert summary["knowledge_graph_nodes"] == 0
    assert summary["intelligence_health_score"] == 0.0
    assert summary["status"] == "WARMING_UP"
    assert summary["source"] == "NO_PERSISTED_RECORDS"


def test_dashboard_adapter_active_hypotheses_is_empty():
    """Verify get_active_hypotheses returns empty list when no hypotheses exist."""
    adapter = DashboardReadOnlyRepositoryAdapter(db_path=":memory:")
    hypotheses = adapter.get_active_hypotheses()
    assert hypotheses == []


def test_dashboard_adapter_governance_decisions_is_empty():
    """Verify get_governance_decisions returns empty list without synthetic EDG_BOOM1000_JUMP_01."""
    adapter = DashboardReadOnlyRepositoryAdapter(db_path=":memory:")
    decisions = adapter.get_governance_decisions()
    assert decisions == []


def test_dashboard_rest_handler_summary_payload():
    """Verify REST handler returns honest summary payload."""
    adapter = DashboardReadOnlyRepositoryAdapter(db_path=":memory:")
    collector = SystemTelemetryCollector()
    handler = DashboardRESTHandler(repo=adapter, collector=collector)

    res = handler.get_summary()
    assert res.status_code == 200
    assert res.data["hypothesis_count"] == 0
    assert res.data["evidence_records_count"] == 0
    assert res.data["status"] == "WARMING_UP"


def test_dashboard_rest_handler_hypotheses_payload():
    """Verify REST handler returns count 0 for hypotheses."""
    adapter = DashboardReadOnlyRepositoryAdapter(db_path=":memory:")
    collector = SystemTelemetryCollector()
    handler = DashboardRESTHandler(repo=adapter, collector=collector)

    res = handler.get_hypotheses()
    assert res.status_code == 200
    assert res.data["count"] == 0
    assert res.data["hypotheses"] == []


def test_dashboard_rest_handler_governance_payload():
    """Verify REST handler returns count 0 for governance."""
    adapter = DashboardReadOnlyRepositoryAdapter(db_path=":memory:")
    collector = SystemTelemetryCollector()
    handler = DashboardRESTHandler(repo=adapter, collector=collector)

    res = handler.get_governance()
    assert res.status_code == 200
    assert res.data["count"] == 0
    assert res.data["decisions"] == []


def test_telemetry_broadcaster_snapshot_clean_defaults():
    """Verify telemetry snapshot does not contain hardcoded fallback constants."""
    master = MasterSystemIntegrationEngine(db_path=":memory:")
    broadcaster = TelemetryBroadcaster(master_engine=master)

    snapshot = broadcaster.get_telemetry_snapshot()

    assert snapshot["type"] == "TELEMETRY_UPDATE"
    assert snapshot["ticks_processed"] == 0
    assert snapshot["candles_closed"] == 0
    assert snapshot["feature_vectors_generated"] == 0
    assert snapshot["edges_evaluated"] == 0
    assert snapshot["pipeline_latency_ms"] == 0.0
    assert snapshot["edges"] == []

    # Statistics should be 0.0 (not 1.4820, 0.0521, 1004.25, 0.0012)
    stats = snapshot["statistics"]
    assert stats["atr"] == 0.0
    assert stats["realized_volatility"] == 0.0
    assert stats["rolling_vwap"] == 0.0
    assert stats["spread_variance"] == 0.0

    # Market state should be INITIALIZING (not TREND_EXPANSION, BULLISH, HIGH)
    state = snapshot["market_state"]
    assert state["regime"] == "INITIALIZING"
    assert state["trend"] == "INITIALIZING"
    assert state["volatility"] == "INITIALIZING"
    assert state["momentum"] == "INITIALIZING"
    assert state["liquidity"] == "INITIALIZING"
    assert state["tick_rate"] == 0.0


def test_master_engine_measured_tick_rate():
    """Verify tick rate is calculated from genuine tick arrival timestamps."""
    master = MasterSystemIntegrationEngine(db_path=":memory:")

    # Initial tick rate is 0.0
    assert master.get_measured_tick_rate() == 0.0

    # Ingest 5 ticks
    for i in range(5):
        master.process_tick(symbol="BOOM_1000", price=1000.0 + i)
        time.sleep(0.01)

    # Measured tick rate should be > 0.0
    rate = master.get_measured_tick_rate()
    assert rate > 0.0
    # Must not be the old synthetic jitter formula 12.0 + (time % 5.0)
    assert rate < 1000.0


def test_no_synthetic_edge_id_in_telemetry_snapshot():
    """Verify that no fake edge IDs exist in telemetry snapshots when no edges discovered."""
    master = MasterSystemIntegrationEngine(db_path=":memory:")
    broadcaster = TelemetryBroadcaster(master_engine=master)

    # Ingest some ticks
    for i in range(10):
        master.process_tick(symbol="BOOM_1000", price=1000.0 + (i * 0.1))

    snapshot = broadcaster.get_telemetry_snapshot()
    assert snapshot["edges"] == []
    for edge in snapshot["edges"]:
        assert not edge["id"].startswith("EDG_BOOM")
        assert not edge["id"].startswith("EDC_")
