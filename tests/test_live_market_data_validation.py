"""
Project GOAT v0.8 — Test Suite: Market Validation Engine (Exhaustive Matrix)
"""

import datetime
import pytest
from goat.marketdata.core.canonical import compute_candle_id, compute_tick_id
from goat.marketdata.core.enums import DerivSymbol, MarketTimeframe
from goat.marketdata.core.models import MarketCandle, MarketTick
from goat.marketdata.validation.engine import MarketValidationEngine
from goat.research.edge.canonical import compute_canonical_sha256

SYMBOLS = [s.value for s in DerivSymbol]
SEQUENCE_NUMBERS = [1, 2, 5, 10, 20, 50, 100]


def get_current_ts(offset_seconds: float = 0.0) -> str:
    dt = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=offset_seconds)
    return dt.isoformat()


def make_valid_tick(symbol: str = "R_100", seq: int = 1, bid: float = 100.0, ask: float = 100.2, ts: str | None = None) -> MarketTick:
    timestamp = ts if ts else get_current_ts()
    tick_id, canonical_hash = compute_tick_id(symbol, "DERIV", bid, ask, timestamp, seq)
    checksum = compute_canonical_sha256(
        {
            "ask": ask,
            "bid": bid,
            "broker": "DERIV",
            "sequence_number": seq,
            "symbol": symbol,
            "timestamp": timestamp,
        }
    )
    return MarketTick(
        tick_id=tick_id,
        symbol=symbol,
        broker="DERIV",
        bid=bid,
        ask=ask,
        spread=round(ask - bid, 8),
        timestamp=timestamp,
        sequence_number=seq,
        source_latency=1.0,
        checksum=checksum,
        metadata={},
        canonical_hash=canonical_hash,
    )


@pytest.mark.parametrize("symbol", SYMBOLS)
@pytest.mark.parametrize("seq", SEQUENCE_NUMBERS[:5])
def test_validation_valid_tick_matrix(symbol, seq):
    engine = MarketValidationEngine(max_allowed_spread=10.0)
    tick = make_valid_tick(symbol=symbol, seq=seq)
    res = engine.validate_tick(tick)
    assert res.is_valid is True


@pytest.mark.parametrize("symbol", SYMBOLS)
def test_validation_duplicate_sequence_matrix(symbol):
    engine = MarketValidationEngine()
    tick = make_valid_tick(symbol=symbol, seq=10)
    res1 = engine.validate_tick(tick)
    assert res1.is_valid is True
    res2 = engine.validate_tick(tick)
    assert res2.is_valid is False
    assert res2.rule_breached == "DUPLICATE_SEQUENCE_NUMBER"


@pytest.mark.parametrize("symbol", SYMBOLS[:5])
def test_validation_checksum_mismatch_matrix(symbol):
    engine = MarketValidationEngine()
    ts = get_current_ts()
    tick_id, canonical_hash = compute_tick_id(symbol, "DERIV", 100.0, 100.2, ts, 1)
    tick = MarketTick(
        tick_id=tick_id,
        symbol=symbol,
        broker="DERIV",
        bid=100.0,
        ask=100.2,
        spread=0.2,
        timestamp=ts,
        sequence_number=1,
        checksum="CORRUPTED_CHECKSUM",
        canonical_hash=canonical_hash,
    )
    res = engine.validate_tick(tick)
    assert res.is_valid is False
    assert res.rule_breached == "CHECKSUM_MISMATCH"


@pytest.mark.parametrize("symbol", SYMBOLS[:5])
@pytest.mark.parametrize("spread", [6.0, 10.0, 50.0])
def test_validation_excessive_spread_matrix(symbol, spread):
    engine = MarketValidationEngine(max_allowed_spread=5.0)
    tick = make_valid_tick(symbol=symbol, bid=100.0, ask=100.0 + spread)
    res = engine.validate_tick(tick)
    assert res.is_valid is False
    assert res.rule_breached == "EXCESSIVE_SPREAD"


@pytest.mark.parametrize("symbol", SYMBOLS[:5])
def test_validation_out_of_order_timestamps_matrix(symbol):
    engine = MarketValidationEngine()
    t1 = make_valid_tick(symbol=symbol, seq=1, ts=get_current_ts(offset_seconds=10.0))
    t2 = make_valid_tick(symbol=symbol, seq=2, ts=get_current_ts(offset_seconds=0.0))

    r1 = engine.validate_tick(t1)
    assert r1.is_valid is True

    r2 = engine.validate_tick(t2)
    assert r2.is_valid is False
    assert r2.rule_breached == "TIMESTAMP_OUT_OF_ORDER"


@pytest.mark.parametrize("symbol", SYMBOLS)
def test_validation_valid_candle_matrix(symbol):
    engine = MarketValidationEngine()
    ts1 = get_current_ts(offset_seconds=-60.0)
    ts2 = get_current_ts()
    cid, chash = compute_candle_id(symbol, "1M", 100.0, 105.0, 99.0, 102.0, ts1, ts2)
    checksum = compute_canonical_sha256(
        {
            "close": 102.0,
            "high": 105.0,
            "low": 99.0,
            "open": 100.0,
            "symbol": symbol,
            "timeframe": "1M",
        }
    )
    candle = MarketCandle(
        candle_id=cid,
        symbol=symbol,
        timeframe=MarketTimeframe.M1,
        open=100.0,
        high=105.0,
        low=99.0,
        close=102.0,
        volume=10.0,
        open_timestamp=ts1,
        close_timestamp=ts2,
        completed=True,
        checksum=checksum,
        metadata={},
        canonical_hash=chash,
    )
    res = engine.validate_candle(candle)
    assert res.is_valid is True
