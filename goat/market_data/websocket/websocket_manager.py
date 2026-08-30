"""
Project GOAT v1.0 — Live Market Data WebSocket Manager

High-level coordinator managing connection resilience, heartbeat monitoring,
subscription recovery, and continuous live tick streaming across all active symbols.
"""

from __future__ import annotations

import asyncio
import datetime
from typing import Callable, Coroutine, Any

from goat.logging import get_logger
from goat.market_data.models.symbol import SUPPORTED_SYMBOLS, get_symbol_config
from goat.market_data.websocket.deriv_client import DerivWebSocketClient
from goat.market_data.websocket.heartbeat import HeartbeatMonitor
from goat.market_data.websocket.reconnect import ReconnectPolicy

_log = get_logger("websocket.manager")


class WebSocketManager:
    """High-level connection manager coordinating streaming client, heartbeat, and reconnection."""

    def __init__(
        self,
        client: DerivWebSocketClient | None = None,
        ping_interval_seconds: float = 20.0,
        max_retries: int = 15,
    ):
        self.client = client or DerivWebSocketClient()
        self.heartbeat = HeartbeatMonitor(ping_interval_seconds=ping_interval_seconds)
        self.reconnect_policy = ReconnectPolicy(max_retries=max_retries)

        self._subscribed_symbols: set[str] = set()  # set of GOAT symbol_ids (e.g. VOLATILITY_100)
        self._connection_state = "DISCONNECTED"  # CONNECTED / DISCONNECTED / RECONNECTING / DEGRADED
        self._connect_time: datetime.datetime | None = None
        self._on_tick_callback: Callable[[dict[str, Any]], Coroutine[Any, Any, None]] | None = None
        self._reconnecting = False

        # Wire client callbacks
        self.client.on_tick = self._handle_client_tick
        self.client.on_disconnected = self._handle_client_disconnected

    @property
    def connection_state(self) -> str:
        """Current high-level connection health status."""
        return self._connection_state

    @property
    def uptime_seconds(self) -> float:
        """Connection uptime in seconds."""
        if self._connect_time and self._connection_state == "CONNECTED":
            return round((datetime.datetime.now(datetime.timezone.utc) - self._connect_time).total_seconds(), 1)
        return 0.0

    @property
    def subscribed_symbols(self) -> list[str]:
        """List of active GOAT symbol IDs currently subscribed."""
        return sorted(list(self._subscribed_symbols))

    def set_on_tick_callback(self, callback: Callable[[dict[str, Any]], Coroutine[Any, Any, None]]) -> None:
        """Register handler for incoming raw tick payloads."""
        self._on_tick_callback = callback

    async def connect(self) -> bool:
        """Connect WebSocket client, start heartbeat monitoring, and recover streams."""
        if self.client.is_connected:
            return True

        self._connection_state = "CONNECTING"
        _log.info("ws_manager_connecting")

        success = await self.client.connect()
        if success:
            self._connection_state = "CONNECTED"
            self._connect_time = datetime.datetime.now(datetime.timezone.utc)
            self.reconnect_policy.record_successful_connection()

            # Start Heartbeat Monitor
            self.heartbeat.start(
                ping_fn=self.client.ping,
                on_timeout_fn=self._trigger_reconnect,
            )

            # Re-subscribe existing symbols if reconnecting
            await self._resubscribe_all()
            _log.info("ws_manager_connected_successfully")
            return True
        else:
            self._connection_state = "DISCONNECTED"
            return False

    async def disconnect(self) -> None:
        """Disconnect WebSocket client and stop heartbeat."""
        _log.info("ws_manager_disconnecting")
        self._connection_state = "DISCONNECTED"
        self._connect_time = None
        await self.heartbeat.stop()
        await self.client.disconnect()
        _log.info("ws_manager_disconnected")

    async def subscribe(self, symbol_id: str) -> bool:
        """Subscribe to market feed for a symbol (GOAT ID or Deriv WS symbol)."""
        cfg = get_symbol_config(symbol_id)
        goat_sym = cfg.symbol_id if cfg else symbol_id.upper()
        deriv_ws_sym = cfg.deriv_ws_symbol if cfg else symbol_id

        self._subscribed_symbols.add(goat_sym)

        if self.client.is_connected:
            try:
                await self.client.subscribe_symbol(deriv_ws_sym)
                _log.info("subscribed_symbol_success", goat_symbol=goat_sym, deriv_ws=deriv_ws_sym)
                return True
            except Exception as exc:
                _log.error("subscribe_symbol_failed", symbol=goat_sym, error=str(exc))
                return False
        return True

    async def unsubscribe(self, symbol_id: str) -> bool:
        """Unsubscribe from market feed for a symbol."""
        cfg = get_symbol_config(symbol_id)
        goat_sym = cfg.symbol_id if cfg else symbol_id.upper()
        deriv_ws_sym = cfg.deriv_ws_symbol if cfg else symbol_id

        self._subscribed_symbols.discard(goat_sym)

        if self.client.is_connected:
            try:
                await self.client.unsubscribe_symbol(deriv_ws_sym)
                _log.info("unsubscribed_symbol_success", goat_symbol=goat_sym)
                return True
            except Exception as exc:
                _log.warning("unsubscribe_symbol_failed", symbol=goat_sym, error=str(exc))
                return False
        return True

    async def subscribe_all_supported(self) -> int:
        """Subscribe to all 8 supported synthetic symbols."""
        count = 0
        for sym_id in SUPPORTED_SYMBOLS.keys():
            res = await self.subscribe(sym_id)
            if res:
                count += 1
        return count

    async def unsubscribe_all(self) -> int:
        """Unsubscribe from all active symbols."""
        symbols = list(self._subscribed_symbols)
        count = 0
        for sym_id in symbols:
            res = await self.unsubscribe(sym_id)
            if res:
                count += 1
        return count

    async def _resubscribe_all(self) -> None:
        """Recover subscriptions following reconnection."""
        if not self._subscribed_symbols:
            return
        _log.info("recovering_subscriptions", count=len(self._subscribed_symbols))
        for goat_sym in list(self._subscribed_symbols):
            cfg = get_symbol_config(goat_sym)
            deriv_ws_sym = cfg.deriv_ws_symbol if cfg else goat_sym
            try:
                await self.client.subscribe_symbol(deriv_ws_sym)
            except Exception as exc:
                _log.error("resubscribe_failed", symbol=goat_sym, error=str(exc))

    async def _handle_client_tick(self, raw_payload: dict[str, Any]) -> None:
        """Route incoming raw client tick to manager callback."""
        self.heartbeat.record_pong()
        if self._on_tick_callback:
            await self._on_tick_callback(raw_payload)

    async def _handle_client_disconnected(self) -> None:
        """Handle client disconnection event."""
        if self._connection_state != "DISCONNECTED" and not self._reconnecting:
            asyncio.create_task(self._trigger_reconnect())

    async def _trigger_reconnect(self) -> None:
        """Execute automatic reconnection workflow with exponential backoff."""
        if self._reconnecting:
            return
        self._reconnecting = True
        self._connection_state = "RECONNECTING"
        await self.heartbeat.stop()

        _log.warning("initiating_reconnection_workflow")
        while self.reconnect_policy.should_retry() and self._connection_state == "RECONNECTING":
            delay = self.reconnect_policy.compute_next_delay()
            _log.info("reconnect_retry_waiting", delay_seconds=delay, attempt=self.reconnect_policy.get_state().attempt_count)
            await asyncio.sleep(delay)

            success = await self.connect()
            if success:
                _log.info("reconnection_successful")
                self._reconnecting = False
                return

        _log.error("reconnection_failed_max_retries_exceeded")
        self._connection_state = "ERROR"
        self._reconnecting = False
