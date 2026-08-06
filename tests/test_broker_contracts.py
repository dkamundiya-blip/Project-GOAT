"""
Project GOAT v0.8 — Test Suite: Broker Adapter Contract & Capability Registry (Exhaustive Matrix)
"""

import pytest

from goat.brokers.contracts.adapter import AbstractBrokerAdapter
from goat.brokers.contracts.registry import BrokerCapabilityRegistry
from goat.brokers.core.canonical import compute_broker_profile_id
from goat.brokers.core.enums import BrokerType, OrderType
from goat.brokers.core.models import BrokerProfile
from goat.marketdata.core.enums import DerivSymbol

SYMBOLS = [s.value for s in DerivSymbol]
ORDER_TYPES = [OrderType.MARKET, OrderType.LIMIT, OrderType.STOP, OrderType.STOP_LIMIT]
STREAM_FLAGS = [True, False]
POSITION_FLAGS = [True, False]


class DummyAdapter(AbstractBrokerAdapter):
    """Dummy concrete adapter for testing AbstractBrokerAdapter interface completeness."""

    def connect(self):
        pass

    def disconnect(self):
        pass

    def heartbeat(self):
        pass

    def get_account(self):
        pass

    def subscribe_market_data(self, symbol: str) -> bool:
        return True

    def unsubscribe_market_data(self, symbol: str) -> bool:
        return True

    def submit_order_intent(self, intent):
        return {}

    def cancel_order(self, order_id: str) -> bool:
        return True

    def modify_order(self, order_id: str, new_stop_loss=None, new_take_profit=None) -> bool:
        return True

    def get_positions(self):
        return []

    def get_open_orders(self):
        return []

    def get_order_history(self, symbol=None):
        return []

    def get_execution_history(self, symbol=None):
        return []

    def health(self):
        pass

    def capabilities(self):
        pass


def test_abstract_broker_adapter_interface():
    adapter = DummyAdapter()
    assert adapter.subscribe_market_data("R_100") is True


@pytest.mark.parametrize("symbol", SYMBOLS)
@pytest.mark.parametrize("order_type", ORDER_TYPES)
@pytest.mark.parametrize("streaming", STREAM_FLAGS)
def test_broker_capability_registry_matrix(symbol, order_type, streaming):
    registry = BrokerCapabilityRegistry()
    b_id, c_hash = compute_broker_profile_id(f"Deriv_{symbol}", "DERIV", "v3")
    profile = BrokerProfile(
        broker_id=b_id,
        broker_name=f"Deriv_{symbol}",
        broker_type=BrokerType.DERIV,
        api_version="v3",
        supported_assets=SYMBOLS,
        supported_order_types=[OrderType.MARKET, OrderType.LIMIT],
        supports_streaming=streaming,
        supports_positions=True,
        supports_history=True,
        metadata={},
        canonical_hash=c_hash,
    )

    registry.register_broker(profile)
    assert registry.get_profile(b_id) == profile
    assert registry.supports_asset(b_id, symbol) is True
    assert registry.supports_streaming(b_id) == streaming

    if order_type in (OrderType.MARKET, OrderType.LIMIT):
        assert registry.supports_order_type(b_id, order_type) is True
    else:
        assert registry.supports_order_type(b_id, order_type) is False
