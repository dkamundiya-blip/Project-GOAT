"""
Project GOAT v0.8 — Abstract Broker Adapter Contract

Defines the mandatory AbstractBrokerAdapter interface that every future broker
implementation (Deriv, Weltrade, MT5, etc.) must implement to connect with GOAT.
Contains zero live network execution logic.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Sequence

from goat.brokers.core.enums import ConnectionStatus
from goat.brokers.core.models import (
    BrokerAccount,
    BrokerConnection,
    BrokerOrderIntent,
    BrokerProfile,
)


class AbstractBrokerAdapter(ABC):
    """Mandatory abstract interface for all broker adapter implementations."""

    @abstractmethod
    def connect(self) -> BrokerConnection:
        """Establish session connection to broker gateway."""
        pass

    @abstractmethod
    def disconnect(self) -> BrokerConnection:
        """Terminate active session connection to broker gateway."""
        pass

    @abstractmethod
    def heartbeat(self) -> BrokerConnection:
        """Send/receive session heartbeat telemetry."""
        pass

    @abstractmethod
    def get_account(self) -> BrokerAccount:
        """Retrieve current broker account balance, equity, and margin state."""
        pass

    @abstractmethod
    def subscribe_market_data(self, symbol: str) -> bool:
        """Subscribe stream subscription for symbol market data."""
        pass

    @abstractmethod
    def unsubscribe_market_data(self, symbol: str) -> bool:
        """Unsubscribe stream subscription for symbol market data."""
        pass

    @abstractmethod
    def submit_order_intent(self, intent: BrokerOrderIntent) -> dict[str, Any]:
        """Submit an unexecuted order intent structure to broker adapter."""
        pass

    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """Request cancellation of an active open order."""
        pass

    @abstractmethod
    def modify_order(self, order_id: str, new_stop_loss: float | None = None, new_take_profit: float | None = None) -> bool:
        """Request modification of active order parameter levels."""
        pass

    @abstractmethod
    def get_positions(self) -> Sequence[dict[str, Any]]:
        """Retrieve active open positions."""
        pass

    @abstractmethod
    def get_open_orders(self) -> Sequence[dict[str, Any]]:
        """Retrieve active working open orders."""
        pass

    @abstractmethod
    def get_order_history(self, symbol: str | None = None) -> Sequence[dict[str, Any]]:
        """Retrieve historical order submission records."""
        pass

    @abstractmethod
    def get_execution_history(self, symbol: str | None = None) -> Sequence[dict[str, Any]]:
        """Retrieve historical execution fill records."""
        pass

    @abstractmethod
    def health(self) -> ConnectionStatus:
        """Evaluate operational connection health status."""
        pass

    @abstractmethod
    def capabilities(self) -> BrokerProfile:
        """Retrieve broker capabilities and profile specifications."""
        pass
