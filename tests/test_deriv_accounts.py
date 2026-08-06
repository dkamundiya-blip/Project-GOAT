"""
Project GOAT v0.8 — Test Suite: Deriv Account Engine (Exhaustive Matrix)
"""

import pytest

from goat.brokers.deriv.accounts.engine import DerivAccountEngine
from goat.marketdata.core.enums import DerivSymbol

SYMBOLS = [s.value for s in DerivSymbol]
BALANCES = [100.0, 500.0, 2500.0, 10000.0, 50000.0]
LOGIN_IDS = ["CR100001", "CR200002", "CR300003"]
CURRENCIES = ["USD", "EUR", "GBP"]


@pytest.mark.parametrize("balance", BALANCES)
@pytest.mark.parametrize("login_id", LOGIN_IDS)
@pytest.mark.parametrize("currency", CURRENCIES)
def test_deriv_account_engine_matrix(balance, login_id, currency):
    engine = DerivAccountEngine(broker_id="BRK_DERIV")
    assert engine.get_latest_account() is None

    bal_json = {
        "balance": {
            "loginid": login_id,
            "currency": currency,
            "balance": balance,
            "equity": balance + 100.0,
            "margin": 50.0,
        }
    }
    snapshot, broker_acc = engine.process_balance_response(bal_json)
    assert snapshot.snapshot_id.startswith("DAC_")
    assert snapshot.login_id == login_id
    assert snapshot.currency == currency
    assert snapshot.balance == balance

    assert broker_acc.account_id.startswith("BAC_")
    assert broker_acc.balance == balance
    assert broker_acc.account_currency == currency
    assert broker_acc.equity == balance + 100.0

    latest = engine.get_latest_account()
    assert latest is not None
    assert latest.account_id == broker_acc.account_id


@pytest.mark.parametrize("symbol", SYMBOLS)
@pytest.mark.parametrize("balance", [1000.0, 5000.0, 25000.0])
def test_deriv_account_engine_symbols_matrix(symbol, balance):
    engine = DerivAccountEngine(broker_id=f"BRK_{symbol}")
    bal_json = {
        "balance": {
            "loginid": f"CR_{symbol}",
            "currency": "USD",
            "balance": balance,
            "equity": balance,
            "margin": 0.0,
        }
    }
    snapshot, broker_acc = engine.process_balance_response(bal_json)
    assert broker_acc.broker_id == f"BRK_{symbol}"
    assert snapshot.login_id == f"CR_{symbol}"
