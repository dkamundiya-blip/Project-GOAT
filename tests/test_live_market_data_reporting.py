"""
Project GOAT v0.8 — Test Suite: Reporting & Executive Reports
"""

import pytest
from goat.marketdata.core.canonical import compute_report_id, compute_tick_id
from goat.marketdata.core.models import MarketTick
from goat.marketdata.reporting.reports import (
    MarketDataExecutiveReport,
    MarketTickReport,
)


def test_market_tick_report_generation():
    rep_id, canonical_hash = compute_report_id("TICK", "2026-07-31T12:00:00Z")
    tick_id, t_hash = compute_tick_id("R_100", "DERIV", 10.0, 10.2, "2026-07-31T12:00:00Z", 1)
    tick = MarketTick(
        tick_id=tick_id,
        symbol="R_100",
        broker="DERIV",
        bid=10.0,
        ask=10.2,
        spread=0.2,
        timestamp="2026-07-31T12:00:00Z",
        sequence_number=1,
        checksum="CHECKSUM",
        canonical_hash=t_hash,
    )

    report = MarketTickReport(
        report_id=rep_id,
        symbol="R_100",
        total_ticks_processed=10,
        average_bid=10.0,
        average_ask=10.2,
        average_spread=0.2,
        latest_tick=tick,
        timestamp="2026-07-31T12:00:00Z",
        canonical_hash=canonical_hash,
    )

    md = report.to_markdown()
    assert "# Market Tick Report — R_100" in md
    assert f"`{rep_id}`" in md

    js = report.to_json()
    assert "report_id" in js
    assert rep_id in js


def test_market_executive_report_generation():
    exec_id, canonical_hash = compute_report_id("EXECUTIVE", "2026-07-31T12:00:00Z")
    report = MarketDataExecutiveReport(
        report_id=exec_id,
        overall_safety_status="HEALTHY",
        active_symbols_count=2,
        total_ticks_ingested=150,
        total_candles_built=10,
        total_gaps_detected=0,
        tick_reports=[],
        stream_reports=[],
        timestamp="2026-07-31T12:00:00Z",
        canonical_hash=canonical_hash,
    )

    md = report.to_markdown()
    assert "Step 7.0 — Live Market Data Infrastructure Executive Report" in md
    assert "`HEALTHY`" in md

    js = report.to_json()
    assert exec_id in js
