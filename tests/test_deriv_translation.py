"""
Project GOAT v0.8 — Test Suite: Deriv Translation Engine (Exhaustive Matrix)
"""

import pytest

from goat.brokers.core.canonical import compute_order_intent_id
from goat.brokers.core.enums import OrderSide, OrderType, TimeInForce
from goat.brokers.core.models import BrokerOrderIntent
from goat.brokers.deriv.core.enums import DerivContractType, DerivDurationUnit
from goat.brokers.deriv.translation.engine import DerivTranslationEngine
from goat.marketdata.core.enums import DerivSymbol, MarketTimeframe

SYMBOLS = [s.value for s in DerivSymbol]
SIDES = [OrderSide.BUY, OrderSide.SELL]
AMOUNTS = [1.0, 10.0, 50.0, 100.0]


@pytest.mark.parametrize("symbol,side,amount", [(sym, s, a) for sym in SYMBOLS for s in SIDES for a in AMOUNTS])
def test_translate_order_intent_matrix(symbol, side, amount):
    translator = DerivTranslationEngine()
    b_id = "BRK_DERIV"
    intent_id, c_hash = compute_order_intent_id(b_id, symbol, side.value, amount, "MARKET", "2026-07-31T12:00:00Z")
    intent = BrokerOrderIntent(
        intent_id=intent_id,
        broker_id=b_id,
        symbol=symbol,
        side=side,
        quantity=amount,
        order_type=OrderType.MARKET,
        time_in_force=TimeInForce.GTC,
        stop_loss=None,
        take_profit=None,
        comment="Test Intent",
        metadata={},
        canonical_hash=c_hash,
    )

    payload_model, req_json = translator.translate_order_intent_to_deriv_payload(intent, duration=5, duration_unit=DerivDurationUnit.TICKS)
    assert payload_model.payload_id.startswith("DOP_")
    assert payload_model.symbol == symbol
    assert payload_model.amount == amount

    expected_contract = DerivContractType.RISE if side == OrderSide.BUY else DerivContractType.FALL
    assert payload_model.contract_type == expected_contract
    assert req_json["proposal"] == 1
    assert req_json["symbol"] == symbol
    assert req_json["contract_type"] == expected_contract.value


@pytest.mark.parametrize("symbol,quote,epoch", [(sym, q, ep) for sym in SYMBOLS for q in [100.0, 1250.5, 9999.9] for ep in [1700000000, 1700000060]])
def test_translate_deriv_tick_matrix(symbol, quote, epoch):
    translator = DerivTranslationEngine()
    tick_json = {
        "tick": {
            "symbol": symbol,
            "quote": quote,
            "epoch": epoch,
            "id": epoch,
        }
    }
    market_tick = translator.translate_deriv_tick_to_market_tick(tick_json)
    assert market_tick.tick_id.startswith("MTK_")
    assert market_tick.symbol == symbol
    assert market_tick.bid == quote


@pytest.mark.parametrize("symbol,granularity", [(sym, g) for sym in SYMBOLS for g in ["60", "300", "3600"]])
def test_translate_deriv_candle_matrix(symbol, granularity):
    translator = DerivTranslationEngine()
    candle_json = {
        "ohlc": {
            "symbol": symbol,
            "open_time": 1700000000,
            "open": 100.0,
            "high": 105.0,
            "low": 95.0,
            "close": 102.0,
            "granularity": granularity,
        }
    }
    candle = translator.translate_deriv_candle_to_market_candle(candle_json)
    assert candle.candle_id.startswith("MCD_")
    assert candle.symbol == symbol
    assert candle.open == 100.0
    assert candle.high == 105.0
    assert candle.low == 95.0
    assert candle.close == 102.0


@pytest.mark.parametrize("login_id,balance", [(lid, b) for lid in ["CR100001", "CR200002"] for b in [100.0, 1000.0, 50000.0]])
def test_translate_deriv_balance_matrix(login_id, balance):
    translator = DerivTranslationEngine()
    bal_json = {
        "balance": {
            "loginid": login_id,
            "currency": "USD",
            "balance": balance,
            "equity": balance + 50.0,
            "margin": 100.0,
        }
    }
    snapshot, broker_acc = translator.translate_deriv_balance_to_account(bal_json)
    assert snapshot.snapshot_id.startswith("DAC_")
    assert snapshot.login_id == login_id
    assert snapshot.balance == balance
    assert broker_acc.account_id.startswith("BAC_")
    assert broker_acc.balance == balance
    assert broker_acc.equity == balance + 50.0


@pytest.mark.parametrize("symbol", SYMBOLS)
@pytest.mark.parametrize("price", [10.0, 50.0, 100.0, 500.0])
def test_translate_execution_response_matrix(symbol, price):
    translator = DerivTranslationEngine()
    mock_json = {
        "buy": {
            "contract_id": f"CON_{symbol}_1001",
            "buy_price": price,
            "payout": round(price * 1.95, 2),
            "transaction_id": f"TX_{symbol}_1",
        }
    }
    exec_model, exec_dict = translator.translate_deriv_execution_response(mock_json, intent_id=f"BOI_{symbol}")
    assert exec_model.execution_id.startswith("DER_")
    assert exec_model.contract_id == f"CON_{symbol}_1001"
    assert exec_model.buy_price == price
    assert exec_dict["status"] == "FILLED"
