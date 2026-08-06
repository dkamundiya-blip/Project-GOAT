"""
Project GOAT v0.8 — Test Suite: Ingestion Engine & Payload Normalization (Exhaustive)
"""

import pytest
from goat.marketdata.core.enums import DerivSymbol
from goat.marketdata.ingestion.engine import MarketIngestionEngine

SYMBOLS = [s.value for s in DerivSymbol]
QUOTES = [0.01, 1.2345, 100.50, 1234.56, 8888.88]
PIP_SIZES = [2, 3, 4, 5]


@pytest.mark.parametrize("symbol", SYMBOLS)
@pytest.mark.parametrize("quote", QUOTES)
@pytest.mark.parametrize("pip_size", PIP_SIZES)
def test_ingestion_deriv_websocket_tick_matrix(symbol, quote, pip_size):
    engine = MarketIngestionEngine(default_broker="DERIV")
    raw_payload = {
        "tick": {
            "symbol": symbol,
            "quote": quote,
            "epoch": 1690000000,
            "pip_size": pip_size,
        }
    }
    res = engine.process_raw_tick(raw_payload, sequence_number=1, source_latency=10.0)
    assert res.success is True
    assert res.tick is not None
    assert res.tick.symbol == symbol
    assert res.tick.bid < res.tick.ask
    assert res.tick.sequence_number == 1


@pytest.mark.parametrize("symbol", SYMBOLS)
@pytest.mark.parametrize("bid", [1.0, 50.0, 100.0])
def test_ingestion_generic_bid_ask_dict_matrix(symbol, bid):
    ask = bid + 0.02
    engine = MarketIngestionEngine(default_broker="DERIV")
    raw_payload = {
        "symbol": symbol,
        "bid": bid,
        "ask": ask,
        "timestamp": "2026-07-31T12:00:00Z",
    }
    res = engine.process_raw_tick(raw_payload, sequence_number=2)
    assert res.success is True
    assert res.tick is not None
    assert res.tick.symbol == symbol
    assert res.tick.bid == bid
    assert res.tick.ask == ask
    assert res.tick.spread == 0.02


@pytest.mark.parametrize(
    "payload, expected_err",
    [
        ({}, "REJECTED_MALFORMED_PAYLOAD"),
        ({"bid": 10.0, "ask": 10.2}, "REJECTED_MISSING_SYMBOL"),
        ({"symbol": "R_100", "bid": -5.0, "ask": 10.0}, "REJECTED_NON_POSITIVE_PRICE"),
        ({"symbol": "R_100", "bid": 10.5, "ask": 10.0}, "REJECTED_NEGATIVE_SPREAD"),
        ({"symbol": "R_100", "quote": "invalid"}, "REJECTED_INVALID_QUOTE"),
        ({"symbol": "R_100", "bid": "nan", "ask": 10.0}, "REJECTED_INVALID_NUMERIC"),
    ],
)
def test_ingestion_malformed_payloads_matrix(payload, expected_err):
    engine = MarketIngestionEngine()
    res = engine.process_raw_tick(payload)
    assert res.success is False
    assert expected_err in res.rejection_reason


@pytest.mark.parametrize("symbol", SYMBOLS)
def test_ingestion_candle_parsing_matrix(symbol):
    engine = MarketIngestionEngine()
    raw_candle = {
        "ohlc": {
            "symbol": symbol,
            "open": 100.0,
            "high": 105.0,
            "low": 98.0,
            "close": 102.0,
            "granularity": "60",
            "open_time": 1690000000,
        }
    }
    res = engine.process_raw_candle(raw_candle)
    assert res.success is True
    assert res.candle is not None
    assert res.candle.symbol == symbol
    assert res.candle.high == 105.0
    assert res.candle.low == 98.0
    assert res.candle.timeframe.value == "1M"


@pytest.mark.parametrize("symbol", SYMBOLS)
def test_ingestion_candle_malformed_matrix(symbol):
    engine = MarketIngestionEngine()
    raw_invalid = {
        "ohlc": {
            "symbol": symbol,
            "open": 100.0,
            "high": 90.0,  # High lower than Open
            "low": 98.0,
            "close": 102.0,
        }
    }
    res = engine.process_raw_candle(raw_invalid)
    assert res.success is False
    assert "REJECTED_INVALID_BOUNDS" in res.rejection_reason
