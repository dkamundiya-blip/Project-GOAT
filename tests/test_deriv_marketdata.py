"""
Project GOAT v0.8 — Test Suite: Deriv Market Data Engine (Exhaustive Matrix)
"""

import pytest

from goat.brokers.deriv.marketdata.engine import DerivMarketDataEngine
from goat.marketdata.core.enums import DerivSymbol

SYMBOLS = [s.value for s in DerivSymbol]
QUOTES = [100.0, 500.5, 1250.75, 9999.0]
EPOCHS = [1700000000, 1700000060, 1700000120, 1700000180]


@pytest.mark.parametrize("symbol", SYMBOLS)
def test_deriv_market_data_engine_subscriptions(symbol):
    engine = DerivMarketDataEngine()
    sub, req = engine.subscribe_symbol(symbol)
    assert sub.subscription_id.startswith("DMS_")
    assert sub.symbol == symbol
    assert sub.is_active is True
    assert req["ticks"] == symbol
    assert req["subscribe"] == 1

    active = engine.get_active_subscriptions()
    assert any(s.symbol == symbol for s in active)

    unsub, u_req = engine.unsubscribe_symbol(symbol)
    assert unsub is not None
    assert unsub.is_active is False
    assert u_req["forget"] == sub.stream_id


@pytest.mark.parametrize("symbol,quote,epoch", [(s, q, ep) for s in SYMBOLS for q in QUOTES for ep in EPOCHS])
def test_deriv_market_data_engine_tick_translation_matrix(symbol, quote, epoch):
    engine = DerivMarketDataEngine()
    tick_json = {"tick": {"symbol": symbol, "quote": quote, "epoch": epoch, "id": epoch}}
    market_tick = engine.process_incoming_tick(tick_json)
    assert market_tick.tick_id.startswith("MTK_")
    assert market_tick.symbol == symbol
    assert market_tick.bid == quote


@pytest.mark.parametrize("symbol", SYMBOLS)
@pytest.mark.parametrize("epoch", EPOCHS)
def test_deriv_market_data_engine_candle_translation_matrix(symbol, epoch):
    engine = DerivMarketDataEngine()
    candle_json = {
        "ohlc": {
            "symbol": symbol,
            "open_time": epoch,
            "open": 100.0,
            "high": 105.0,
            "low": 95.0,
            "close": 102.0,
            "granularity": "60",
        }
    }
    market_candle = engine.process_incoming_candle(candle_json)
    assert market_candle.candle_id.startswith("MCD_")
    assert market_candle.symbol == symbol
    assert market_candle.open == 100.0


def test_unsupported_symbol_subscription_failure():
    engine = DerivMarketDataEngine()
    with pytest.raises(ValueError):
        engine.subscribe_symbol("INVALID_SYMBOL_123")
