"""
Project GOAT v0.8 — Test Suite: Broker Account Engine (Exhaustive Matrix)
"""

import pytest
from goat.brokers.account.engine import BrokerAccountEngine
from goat.marketdata.core.enums import DerivSymbol

SYMBOLS = [s.value for s in DerivSymbol]
BALANCES = [100.0, 1000.0, 5000.0, 50000.0]
LEVERAGES = [1.0, 10.0, 50.0, 100.0, 500.0]
PNLS = [-500.0, -50.0, 0.0, 100.0, 2500.0]
DEPOSITS = [100.0, 500.0, 1000.0, 5000.0]


@pytest.mark.parametrize("balance", BALANCES)
@pytest.mark.parametrize("leverage", LEVERAGES)
@pytest.mark.parametrize("pnl", PNLS)
def test_broker_account_engine_matrix(balance, leverage, pnl):
    engine = BrokerAccountEngine(broker_id="BRK_DERIV12345678", initial_balance=balance, currency="USD", leverage=leverage)
    engine.update_unrealized_pnl(pnl)
    engine.update_used_margin(100.0)

    account = engine.get_account_snapshot()
    assert account.broker_id == "BRK_DERIV12345678"
    assert account.balance == balance
    assert account.equity == max(0.0, round(balance + pnl, 2))
    assert account.leverage == leverage
    assert account.margin == 100.0
    assert account.free_margin == max(0.0, round(account.equity - 100.0, 2))


@pytest.mark.parametrize("symbol", SYMBOLS)
@pytest.mark.parametrize("deposit", DEPOSITS)
def test_broker_account_deposit_withdrawal_matrix(symbol, deposit):
    b_id = f"BRK_{symbol}"
    engine = BrokerAccountEngine(broker_id=b_id, initial_balance=1000.0)
    engine.update_balance(deposit)
    snap1 = engine.get_account_snapshot()
    assert snap1.balance == 1000.0 + deposit

    engine.update_balance(-deposit)
    snap2 = engine.get_account_snapshot()
    assert snap2.balance == 1000.0
