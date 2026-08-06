"""
Project GOAT v0.8 — Broker Capability Registry

Registry describing supported assets, order types, streaming, positions,
history, stop loss, take profit, modification, and cancellation capabilities
across registered broker implementations.
"""

from __future__ import annotations

from typing import Sequence

from goat.brokers.core.enums import OrderType
from goat.brokers.core.models import BrokerProfile


class BrokerCapabilityRegistry:
    """Registry maintaining broker profiles and verifying adapter capability contracts."""

    def __init__(self):
        self._profiles: dict[str, BrokerProfile] = {}

    def register_broker(self, profile: BrokerProfile) -> None:
        """Register a broker profile into the capability registry."""
        self._profiles[profile.broker_id] = profile

    def get_profile(self, broker_id: str) -> BrokerProfile | None:
        """Retrieve registered broker profile by broker ID."""
        return self._profiles.get(broker_id)

    def list_registered_brokers(self) -> Sequence[BrokerProfile]:
        """List all registered broker profiles sorted by broker_id."""
        return sorted(list(self._profiles.values()), key=lambda p: p.broker_id)

    def supports_asset(self, broker_id: str, symbol: str) -> bool:
        """Check if broker supports trading a given asset symbol."""
        profile = self.get_profile(broker_id)
        if not profile:
            return False
        return symbol.strip().upper() in [s.strip().upper() for s in profile.supported_assets]

    def supports_order_type(self, broker_id: str, order_type: OrderType) -> bool:
        """Check if broker supports a specific OrderType."""
        profile = self.get_profile(broker_id)
        if not profile:
            return False
        return order_type in profile.supported_order_types

    def supports_streaming(self, broker_id: str) -> bool:
        """Check if broker supports real-time market data streaming."""
        profile = self.get_profile(broker_id)
        return profile.supports_streaming if profile else False

    def supports_positions(self, broker_id: str) -> bool:
        """Check if broker supports position tracking."""
        profile = self.get_profile(broker_id)
        return profile.supports_positions if profile else False

    def supports_history(self, broker_id: str) -> bool:
        """Check if broker supports historical bar data retrieval."""
        profile = self.get_profile(broker_id)
        return profile.supports_history if profile else False
