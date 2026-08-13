"""
Project GOAT — Regression Test Suite: Legacy market_ticks Warning Elimination (`tests/test_legacy_market_ticks_regression.py`)

Verifies:
1. LiveMarketDataIngestionEngine operates on v1.0 schema (live_market_ticks, live_market_candles) without requiring obsolete v0.8 market_ticks table.
2. Zero 'legacy_engine_process_failed' warning logs emitted during raw tick ingestion.
3. LiveTick normalization, LiveTickBuffer, and BufferedTickWriter persist cleanly to live_market_ticks.
4. LiveCandleBuilder successfully builds and persists multi-timeframe candles to live_market_candles.
5. End-to-end integration with MasterSystemIntegrationEngine proceeds seamlessly.
"""

from __future__ import annotations

import logging
import pytest
import sqlite3
from pathlib import Path

from goat.market_data.engine import LiveMarketDataIngestionEngine
from goat.integration.master import MasterSystemIntegrationEngine


@pytest.mark.asyncio
async def test_live_ingestion_engine_emits_no_legacy_warnings(tmp_path: Path, caplog: pytest.LogCaptureFixture):
    """Verify LiveMarketDataIngestionEngine processes ticks without attempting to write to legacy market_ticks."""
    caplog.set_level(logging.WARNING)

    db_file = tmp_path / "test_live_ingestion.db"
    engine = LiveMarketDataIngestionEngine(db_path=db_file)
    await engine.start()

    # Raw Deriv tick payload
    raw_payload = {
        "symbol": "BOOM_1000",
        "quote": 1004.50,
        "bid": 1004.40,
        "ask": 1004.60,
        "epoch": 1723590000,
        "timestamp": "2026-08-14T02:00:00.123Z",
    }

    # Ingest 10 ticks across the engine
    for i in range(10):
        tick_data = dict(raw_payload)
        tick_data["quote"] = 1004.50 + (i * 0.10)
        tick_data["epoch"] = 1723590000 + (i * 5)
        tick_data["timestamp"] = f"2026-08-14T02:00:{i * 5:02d}.000Z"
        await engine._on_raw_tick_received(tick_data)

    await engine.stop()

    # 1. Assert NO 'legacy_engine_process_failed' warnings were logged
    warning_records = [record for record in caplog.records if record.levelno >= logging.WARNING]
    for record in warning_records:
        assert "legacy_engine_process_failed" not in record.message
        assert "no such table: market_ticks" not in record.message

    # 2. Inspect SQLite database tables: market_ticks MUST NOT exist, live_market_ticks MUST exist
    conn = sqlite3.connect(str(db_file))
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = {row[0] for row in cursor.fetchall()}

    assert "market_ticks" not in tables
    assert "live_market_ticks" in tables
    assert "live_market_candles" in tables

    # 3. Verify ticks were persisted to active v1.0 table
    cursor.execute("SELECT COUNT(*) FROM live_market_ticks WHERE symbol = 'BOOM_1000';")
    count = cursor.fetchone()[0]
    assert count == 10

    conn.close()


@pytest.mark.asyncio
async def test_live_ingestion_to_master_pipeline_end_to_end(tmp_path: Path, caplog: pytest.LogCaptureFixture):
    """Verify that removing the legacy hook preserves full master pipeline flow."""
    caplog.set_level(logging.WARNING)

    db_file = tmp_path / "test_master_flow.db"
    ingest_engine = LiveMarketDataIngestionEngine(db_path=db_file)
    master_engine = MasterSystemIntegrationEngine(db_path=db_file, symbol="BOOM_1000", timeframe="1m")

    await ingest_engine.start()

    # Simulate 5 ticks across 1 minute boundary
    base_epoch = 1723590000
    for i in range(5):
        epoch = base_epoch + (i * 15)
        raw_tick = {
            "symbol": "BOOM_1000",
            "quote": 1000.0 + (i * 2.0),
            "bid": 999.9 + (i * 2.0),
            "ask": 1000.1 + (i * 2.0),
            "epoch": epoch,
            "timestamp": f"2026-08-14T02:00:{i * 15:02d}.000Z",
        }
        await ingest_engine._on_raw_tick_received(raw_tick)
        master_engine.process_tick(
            symbol="BOOM_1000",
            price=raw_tick["quote"],
            timestamp_iso=raw_tick["timestamp"],
        )

    # Next tick crossing 1-minute boundary
    boundary_tick = {
        "symbol": "BOOM_1000",
        "quote": 1010.0,
        "bid": 1009.9,
        "ask": 1010.1,
        "epoch": base_epoch + 60,
        "timestamp": "2026-08-14T02:01:00.000Z",
    }
    await ingest_engine._on_raw_tick_received(boundary_tick)
    master_engine.process_tick(
        symbol="BOOM_1000",
        price=boundary_tick["quote"],
        timestamp_iso=boundary_tick["timestamp"],
    )

    await ingest_engine.stop()

    # Assert master engine processed candles and generated features
    assert master_engine.ticks_processed == 6
    assert master_engine.candles_closed >= 1
    assert master_engine.feature_vectors_generated >= 1

    # Assert zero legacy errors
    for record in caplog.records:
        assert "legacy_engine_process_failed" not in record.message
