"""
Project GOAT v0.8 — Deriv Market Data Engine

Manages symbol subscriptions, unsubscriptions, and translates incoming Deriv WebSocket stream payloads
into Step 7.0 normalized MarketTick and MarketCandle models.
"""

from __future__ import annotations

from typing import Any, Sequence

from goat.brokers.deriv.core.canonical import compute_deriv_subscription_id
from goat.brokers.deriv.core.models import DerivMarketSubscription
from goat.brokers.deriv.translation.engine import DerivTranslationEngine
from goat.marketdata.core.enums import DerivSymbol
from goat.marketdata.core.models import MarketCandle, MarketTick

SUPPORTED_DERIV_SYMBOLS = [s.value for s in DerivSymbol]


class DerivMarketDataEngine:
    """Engine managing market data subscriptions and stream translation for Deriv Synthetic Indices."""

    def __init__(self, translation_engine: DerivTranslationEngine | None = None):
        self.translator = translation_engine or DerivTranslationEngine()
        self._subscriptions: dict[str, DerivMarketSubscription] = {}
        self._request_counter: int = 1000

    def subscribe_symbol(self, symbol: str) -> tuple[DerivMarketSubscription, dict[str, Any]]:
        """Create stream subscription for symbol and return subscription model & Deriv JSON request."""
        sym_clean = str(symbol).strip().upper()
        if sym_clean not in SUPPORTED_DERIV_SYMBOLS:
            raise ValueError(f"Symbol '{sym_clean}' is not a supported Deriv Synthetic Index")

        self._request_counter += 1
        req_id = self._request_counter

        sub_id, canonical_hash = compute_deriv_subscription_id(sym_clean, req_id)
        subscription = DerivMarketSubscription(
            subscription_id=sub_id,
            symbol=sym_clean,
            request_id=req_id,
            is_active=True,
            stream_id=f"STR_{sym_clean}_{req_id}",
            metadata={},
            canonical_hash=canonical_hash,
        )
        self._subscriptions[sym_clean] = subscription

        deriv_request_json = {
            "ticks": sym_clean,
            "subscribe": 1,
            "req_id": req_id,
        }

        return subscription, deriv_request_json

    def unsubscribe_symbol(self, symbol: str) -> tuple[DerivMarketSubscription | None, dict[str, Any]]:
        """Unsubscribe stream subscription for symbol."""
        sym_clean = str(symbol).strip().upper()
        sub = self._subscriptions.get(sym_clean)
        if not sub:
            return None, {"forget_all": "ticks"}

        self._request_counter += 1
        req_id = self._request_counter

        unsub_id, canonical_hash = compute_deriv_subscription_id(sym_clean, req_id)
        updated_sub = DerivMarketSubscription(
            subscription_id=unsub_id,
            symbol=sym_clean,
            request_id=req_id,
            is_active=False,
            stream_id="",
            metadata={},
            canonical_hash=canonical_hash,
        )
        self._subscriptions.pop(sym_clean, None)

        deriv_request_json = {
            "forget": sub.stream_id,
            "req_id": req_id,
        }

        return updated_sub, deriv_request_json

    def process_incoming_tick(self, tick_json: dict[str, Any]) -> MarketTick:
        """Process incoming raw Deriv tick JSON into Step 7.0 MarketTick."""
        return self.translator.translate_deriv_tick_to_market_tick(tick_json)

    def process_incoming_candle(self, candle_json: dict[str, Any]) -> MarketCandle:
        """Process incoming raw Deriv candle JSON into Step 7.0 MarketCandle."""
        return self.translator.translate_deriv_candle_to_market_candle(candle_json)

    def get_active_subscriptions(self) -> Sequence[DerivMarketSubscription]:
        """Retrieve list of currently active market subscriptions."""
        return sorted(list(self._subscriptions.values()), key=lambda s: s.symbol)
