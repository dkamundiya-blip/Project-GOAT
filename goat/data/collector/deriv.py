"""
Project GOAT v0.2 — Deriv Concrete Market Data Collector

Asynchronous WebSocket collector for Deriv synthetic index market data.
Implements request-response correlation (req_id), connection resilience with bounded
exponential backoff, heartbeat health monitoring, subscription lifecycle tracking,
and normalization into canonical GOAT Tick schema.
"""

from __future__ import annotations

import asyncio
import json
import random
from collections.abc import AsyncIterator
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

import websockets
from websockets.exceptions import ConnectionClosed

from goat.config import GoatSettings
from goat.data.collector.base import AbstractCollector, CollectorStatus
from goat.data.collector.deriv_schemas import DerivTickPayload
from goat.data.schemas import DataSource, Tick
from goat.logging import get_logger

_log = get_logger("collector.deriv")


class DerivMarketDataCollector(AbstractCollector):
    """Concrete MarketDataCollector for Deriv WebSocket API.

    Args:
        settings: GoatSettings configuration instance.
        ws_endpoint: Optional override URL for Deriv WebSocket API.
        app_id: Optional override app_id.
    """

    def __init__(
        self,
        settings: GoatSettings | None = None,
        ws_endpoint: str | None = None,
        app_id: int | None = None,
    ) -> None:
        self._settings = settings or GoatSettings()
        self._endpoint = ws_endpoint or self._settings.deriv_ws_endpoint
        self._app_id = app_id or self._settings.deriv_app_id

        self._url = f"{self._endpoint}?app_id={self._app_id}"
        self._status = CollectorStatus.DISCONNECTED

        self._ws: websockets.WebSocketClientProtocol | None = None
        self._req_id_counter = 0

        # Correlation: req_id -> Future[dict[str, Any]]
        self._pending_requests: dict[int, asyncio.Future[dict[str, Any]]] = {}

        # Subscriptions: symbol -> subscription_id
        self._active_subscriptions: dict[str, str] = {}

        # Queues per symbol for streaming ticks: symbol -> asyncio.Queue[Tick]
        self._tick_queues: dict[str, asyncio.Queue[Tick]] = {}

        # Background tasks
        self._message_task: asyncio.Task[None] | None = None
        self._heartbeat_task: asyncio.Task[None] | None = None

        self._reconnect_count = 0
        self._shutdown_requested = False

    async def connect(self) -> None:
        """Establish WebSocket connection to Deriv API with resilience retries."""
        if self._status in (CollectorStatus.CONNECTED, CollectorStatus.CONNECTING):
            return

        self._shutdown_requested = False
        self._status = CollectorStatus.CONNECTING
        _log.info("deriv_collector_connecting", url=self._url)

        attempt = 0
        while not self._shutdown_requested:
            try:
                self._ws = await websockets.connect(
                    self._url,
                    open_timeout=self._settings.connection_timeout,
                    close_timeout=self._settings.connection_timeout,
                )
                self._status = CollectorStatus.CONNECTED
                _log.info("deriv_collector_connected")

                # Start background tasks
                self._message_task = asyncio.create_task(self._message_loop())
                self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

                # Re-subscribe to any previously active subscriptions
                await self._resubscribe_all()
                return

            except Exception as exc:
                attempt += 1
                self._reconnect_count += 1
                if attempt > self._settings.reconnect_max_retries:
                    self._status = CollectorStatus.ERROR
                    _log.error(
                        "deriv_connection_failed_max_retries",
                        retries=attempt,
                        error=str(exc),
                    )
                    raise ConnectionError(
                        f"Failed to connect to Deriv API after {attempt} attempts: {exc}"
                    ) from exc

                # Bounded exponential backoff with jitter
                delay = min(
                    self._settings.reconnect_max_delay,
                    self._settings.reconnect_base_delay * (2 ** (attempt - 1)),
                )
                jitter = random.uniform(0, 0.5 * delay)
                total_delay = delay + jitter

                _log.warning(
                    "deriv_connection_retry",
                    attempt=attempt,
                    delay_seconds=round(total_delay, 2),
                    error=str(exc),
                )
                await asyncio.sleep(total_delay)

    async def disconnect(self) -> None:
        """Gracefully close WebSocket connection and release background tasks."""
        if self._shutdown_requested and self._status == CollectorStatus.DISCONNECTED:
            return

        _log.info("deriv_collector_disconnecting")
        self._shutdown_requested = True
        self._status = CollectorStatus.DISCONNECTED

        # Unsubscribe all active streams gracefully
        for symbol, sub_id in list(self._active_subscriptions.items()):
            try:
                await self.unsubscribe_ticks(symbol)
            except Exception:
                pass

        # Cancel background tasks
        tasks_to_cancel = []
        if self._heartbeat_task and not self._heartbeat_task.done():
            tasks_to_cancel.append(self._heartbeat_task)
        if self._message_task and not self._message_task.done():
            tasks_to_cancel.append(self._message_task)

        for t in tasks_to_cancel:
            t.cancel()
            try:
                await t
            except (asyncio.CancelledError, Exception):
                pass

        # Fail any pending futures
        for req_id, fut in self._pending_requests.items():
            if not fut.done():
                fut.set_exception(ConnectionError("Collector disconnected"))
        self._pending_requests.clear()

        # Close WebSocket connection
        if self._ws is not None:
            try:
                await self._ws.close()
            except Exception:
                pass
            self._ws = None

        _log.info("deriv_collector_disconnected", reconnect_count=self._reconnect_count)

    async def get_status(self) -> CollectorStatus:
        """Return current collector connection status."""
        return self._status

    @property
    def reconnect_count(self) -> int:
        """Return cumulative reconnect count."""
        return self._reconnect_count

    def _next_req_id(self) -> int:
        """Generate auto-incrementing request ID for correlation."""
        self._req_id_counter += 1
        return self._req_id_counter

    async def request(self, payload: dict[str, Any], timeout: float = 10.0) -> dict[str, Any]:
        """Send a JSON request over WebSocket and await matching response via req_id.

        Args:
            payload: Request dictionary to send over WebSocket.
            timeout: Max seconds to wait for matching response.

        Returns:
            Matching response dictionary from provider.
        """
        if self._status != CollectorStatus.CONNECTED or self._ws is None:
            raise ConnectionError("Deriv collector is not connected")

        req_id = self._next_req_id()
        payload_with_id = {**payload, "req_id": req_id}

        loop = asyncio.get_running_loop()
        fut: asyncio.Future[dict[str, Any]] = loop.create_future()
        self._pending_requests[req_id] = fut

        try:
            raw_msg = json.dumps(payload_with_id)
            await self._ws.send(raw_msg)
            return await asyncio.wait_for(fut, timeout=timeout)
        except asyncio.TimeoutError:
            _log.error("deriv_request_timeout", req_id=req_id, payload=payload)
            raise TimeoutError(f"Deriv API request timed out (req_id={req_id})")
        finally:
            self._pending_requests.pop(req_id, None)

    async def subscribe_ticks(self, symbol: str) -> str:
        """Subscribe to live tick stream for a symbol.

        Args:
            symbol: Provider instrument identifier (e.g. ``"R_75"``).

        Returns:
            Subscription ID string.
        """
        if symbol in self._active_subscriptions:
            _log.debug("already_subscribed_to_symbol", symbol=symbol)
            return self._active_subscriptions[symbol]

        _log.info("subscribing_to_ticks", symbol=symbol)
        resp = await self.request({"ticks": symbol, "subscribe": 1})

        if "error" in resp:
            err_msg = resp["error"].get("message", "Unknown subscription error")
            _log.error("subscription_error", symbol=symbol, error=err_msg)
            raise RuntimeError(f"Subscription failed for {symbol}: {err_msg}")

        sub_info = resp.get("subscription", {})
        sub_id = str(sub_info.get("id") or resp.get("tick", {}).get("id") or f"sub_{symbol}")
        self._active_subscriptions[symbol] = sub_id

        if symbol not in self._tick_queues:
            self._tick_queues[symbol] = asyncio.Queue()

        _log.info("subscribed_to_ticks", symbol=symbol, subscription_id=sub_id)
        return sub_id

    async def unsubscribe_ticks(self, symbol: str) -> None:
        """Unsubscribe from live tick stream for a symbol."""
        sub_id = self._active_subscriptions.pop(symbol, None)
        if sub_id and self._status == CollectorStatus.CONNECTED and self._ws is not None:
            _log.info("unsubscribing_from_ticks", symbol=symbol, subscription_id=sub_id)
            try:
                await self.request({"forget": sub_id})
            except Exception as exc:
                _log.warning("unsubscribe_request_failed", symbol=symbol, error=str(exc))

    async def _resubscribe_all(self) -> None:
        """Re-establish active subscriptions after reconnection."""
        symbols_to_resub = list(self._active_subscriptions.keys())
        self._active_subscriptions.clear()
        for symbol in symbols_to_resub:
            try:
                await self.subscribe_ticks(symbol)
            except Exception as exc:
                _log.error("resubscribe_failed", symbol=symbol, error=str(exc))

    async def collect_ticks(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
    ) -> AsyncIterator[Tick]:
        """Yield live ticks for the given symbol between start and end times.

        Subscribes to symbol if not already subscribed. Yields ticks until end time
        or until collector is disconnected.
        """
        if self._status != CollectorStatus.CONNECTED:
            raise RuntimeError("DerivMarketDataCollector is not connected")

        await self.subscribe_ticks(symbol)
        queue = self._tick_queues[symbol]

        start_utc = start.astimezone(timezone.utc)
        end_utc = end.astimezone(timezone.utc)

        while not self._shutdown_requested:
            now = datetime.now(timezone.utc)
            if now >= end_utc:
                break

            try:
                tick = await asyncio.wait_for(queue.get(), timeout=1.0)
                if tick.timestamp >= start_utc:
                    yield tick
            except asyncio.TimeoutError:
                continue

    async def _message_loop(self) -> None:
        """Continuously receive and route WebSocket messages."""
        while self._status == CollectorStatus.CONNECTED and self._ws is not None:
            try:
                raw_data = await self._ws.recv()
                msg = json.loads(raw_data)
                self._handle_message(msg)
            except ConnectionClosed:
                _log.warning("deriv_websocket_connection_closed")
                if not self._shutdown_requested:
                    asyncio.create_task(self._trigger_reconnect())
                break
            except asyncio.CancelledError:
                break
            except Exception as exc:
                _log.warning("malformed_or_error_message", error=str(exc))

    def _handle_message(self, msg: dict[str, Any]) -> None:
        """Parse and route individual message dictionary."""
        # 1. Match request correlation via req_id
        req_id = msg.get("req_id")
        if isinstance(req_id, int) and req_id in self._pending_requests:
            fut = self._pending_requests.get(req_id)
            if fut and not fut.done():
                fut.set_result(msg)

        # 2. Check msg_type for live tick stream
        msg_type = msg.get("msg_type")
        if msg_type == "tick" and "tick" in msg:
            try:
                payload = DerivTickPayload.from_tick_dict(msg["tick"])
                tick = payload.to_goat_tick(source=DataSource.LIVE)

                if payload.symbol in self._tick_queues:
                    queue = self._tick_queues[payload.symbol]
                    if queue.full():
                        try:
                            queue.get_nowait()
                        except asyncio.QueueEmpty:
                            pass
                    queue.put_nowait(tick)

            except Exception as exc:
                _log.warning("failed_to_parse_live_tick", error=str(exc))

    async def _heartbeat_loop(self) -> None:
        """Periodically send ping to verify connection health."""
        if self._settings.heartbeat_interval <= 0:
            return
        while self._status == CollectorStatus.CONNECTED:
            try:
                await asyncio.sleep(self._settings.heartbeat_interval)
                if self._status == CollectorStatus.CONNECTED:
                    await self.request({"ping": 1}, timeout=5.0)
            except asyncio.CancelledError:
                break
            except Exception as exc:
                _log.warning("heartbeat_ping_failed", error=str(exc))

    async def _trigger_reconnect(self) -> None:
        """Trigger reconnection workflow after connection drop."""
        self._status = CollectorStatus.DISCONNECTED
        try:
            await self.connect()
        except Exception as exc:
            _log.error("reconnect_workflow_failed", error=str(exc))
