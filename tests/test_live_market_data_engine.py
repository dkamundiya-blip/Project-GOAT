"""
Project GOAT v0.8 — Test Suite: LiveMarketDataEngine Coordinator Integration (Exhaustive Matrix)
"""

import datetime
import sqlite3
import pytest

from goat.marketdata.core.enums import DerivSymbol, SafetyGateStatus
from goat.marketdata.engine import LiveMarketDataEngine
from goat.marketdata.persistence.repository import init_marketdata_db

SYMBOLS = [s.value for s in DerivSymbol]


@pytest.fixture
def engine():
    conn = init_marketdata_db(":memory:")
    eng = LiveMarketDataEngine(db_conn=conn, default_broker="DERIV")
    yield eng
    conn.close()


@pytest.mark.parametrize("symbol", SYMBOLS)
def test_live_market_data_engine_tick_pipeline_matrix(engine, symbol):
    now_epoch = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
    raw_payload_1 = {
        "tick": {
            "symbol": symbol,
            "quote": 1234.56,
            "epoch": now_epoch,
            "pip_size": 2,
        }
    }

    out1 = engine.process_raw_tick(raw_payload_1, source_latency=5.0)
    assert out1.ingestion_success is True
    assert out1.validation_success is True
    assert out1.tick is not None
    assert out1.tick.symbol == symbol
    assert out1.tick.sequence_number == 1
    assert out1.gap_detected is None
    assert out1.safety_status in (SafetyGateStatus.HEALTHY, SafetyGateStatus.UNAVAILABLE)

    # Second tick
    raw_payload_2 = {
        "tick": {
            "symbol": symbol,
            "quote": 1235.00,
            "epoch": now_epoch + 1,
            "pip_size": 2,
        }
    }

    out2 = engine.process_raw_tick(raw_payload_2, source_latency=10.0)
    assert out2.ingestion_success is True
    assert out2.validation_success is True
    assert out2.tick.sequence_number == 2


@pytest.mark.parametrize("symbol", SYMBOLS)
def test_live_market_data_engine_executive_report_matrix(engine, symbol):
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    raw_tick = {
        "symbol": symbol,
        "bid": 1.0850,
        "ask": 1.0852,
        "timestamp": now_iso,
    }
    out = engine.process_raw_tick(raw_tick)
    assert out.ingestion_success is True
    assert out.validation_success is True

    exec_rep = engine.generate_executive_report()
    assert exec_rep.active_symbols_count >= 1
    assert exec_rep.total_ticks_ingested >= 1
    assert len(exec_rep.tick_reports) >= 1
    assert len(exec_rep.stream_reports) >= 1
