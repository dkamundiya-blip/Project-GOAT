"""
Project GOAT v1.0 — Deriv Live WebSocket Client

Low-level asynchronous client managing WebSocket connection to Deriv API,
request-response correlation (req_id), message receiving loop, and stream subscriptions.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any, Callable, Coroutine
import websockets
from websockets.exceptions import ConnectionClosed

from goat.config import GoatSettings
from goat.logging import get_logger

_log = get_logger("websocket.deriv_client")


class DerivWebSocketClient:
    """Asynchronous WebSocket client for Deriv synthetic indices stream."""

    def __init__(
        self,
        endpoint_url: str | None = None,
        app_id: int | None = None,
        connection_timeout: float = 10.0,
    ):
        settings = GoatSettings()
        self.endpoint_url = endpoint_url or settings.deriv_ws_endpoint
        self.app_id = app_id or settings.deriv_app_id
        self.connection_timeout = connection_timeout
        self.url = f"{self.endpoint_url}?app_id={self.app_id}"

        self._ws: websockets.WebSocketClientProtocol | None = None
        self._req_id_counter = 0
        self._pending_requests: dict[int, asyncio.Future[dict[str, Any]]] = {}
        self._active_subscriptions: dict[str, str] = {}  # symbol -> sub_id
        self._message_task: asyncio.Task[None] | None = None
        self._is_connected = False
        self._connection_id = "DERIV_WS_01"

        # Event Callbacks
        self.on_tick: Callable[[dict[str, Any]], Coroutine[Any, Any, None]] | None = None
        self.on_connected: Callable[[], Coroutine[Any, Any, None]] | None = None
        self.on_disconnected: Callable[[], Coroutine[Any, Any, None]] | None = None
        self.on_error: Callable[[str], Coroutine[Any, Any, None]] | None = None

    @property
    def is_connected(self) -> bool:
        """True if WebSocket socket connection is active."""
        return self._is_connected and self._ws is not None

    def _next_req_id(self) -> int:
        """Generate incrementing request correlation ID."""
        self._req_id_counter += 1
        return self._req_id_counter

    async def connect(self) -> bool:
        """Establish WebSocket connection and start background receiver loop."""
        if self.is_connected:
            return True

        _log.info("deriv_client_connecting", url=self.url)
        try:
            self._ws = await websockets.connect(
                self.url,
                open_timeout=self.connection_timeout,
                close_timeout=self.connection_timeout,
            )
            self._is_connected = True
            self._message_task = asyncio.create_task(self._message_loop())
            _log.info("deriv_client_connected")

            if self.on_connected:
                await self.on_connected()
            return True
        except Exception as exc:
            self._is_connected = False
            _log.error("deriv_client_connection_failed", error=str(exc))
            if self.on_error:
                await self.on_error(str(exc))
            return False

    async def disconnect(self) -> None:
        """Gracefully close WebSocket connection."""
        if not self._is_connected:
            return

        _log.info("deriv_client_disconnecting")
        self._is_connected = False

        if self._message_task and not self._message_task.done():
            self._message_task.cancel()
            try:
                await self._message_task
            except (asyncio.CancelledError, Exception):
                pass

        for req_id, fut in list(self._pending_requests.items()):
            if not fut.done():
                fut.set_exception(ConnectionError("Client disconnected"))
        self._pending_requests.clear()

        if self._ws:
            try:
                await self._ws.close()
            except Exception:
                pass
            self._ws = None

        if self.on_disconnected:
            await self.on_disconnected()
        _log.info("deriv_client_disconnected")

    async def request(self, payload: dict[str, Any], timeout: float = 10.0) -> dict[str, Any]:
        """Send JSON payload and await matching response via req_id."""
        if not self.is_connected or self._ws is None:
            raise ConnectionError("DerivWebSocketClient is not connected")

        req_id = self._next_req_id()
        payload_with_id = {**payload, "req_id": req_id}

        loop = asyncio.get_running_loop()
        fut: asyncio.Future[dict[str, Any]] = loop.create_future()
        self._pending_requests[req_id] = fut

        try:
            msg_str = json.dumps(payload_with_id)
            await self._ws.send(msg_str)
            return await asyncio.wait_for(fut, timeout=timeout)
        except asyncio.TimeoutError:
            _log.error("request_timeout", req_id=req_id, payload=payload)
            raise TimeoutError(f"Request timed out (req_id={req_id})")
        finally:
            self._pending_requests.pop(req_id, None)

    async def ping(self) -> bool:
        """Send ping request to provider."""
        try:
            res = await self.request({"ping": 1}, timeout=5.0)
            return res.get("ping") == "pong"
        except Exception:
            return False

    async def subscribe_symbol(self, deriv_ws_symbol: str) -> str:
        """Subscribe to streaming tick prices for a symbol.

        Args:
            deriv_ws_symbol: Deriv symbol identifier (e.g. R_100, stpRNG).

        Returns:
            Subscription ID string.
        """
        if deriv_ws_symbol in self._active_subscriptions:
            return self._active_subscriptions[deriv_ws_symbol]

        _log.info("subscribing_deriv_symbol", symbol=deriv_ws_symbol)
        resp = await self.request({"ticks": deriv_ws_symbol, "subscribe": 1})

        if "error" in resp:
            err_msg = resp["error"].get("message", "Subscription error")
            _log.error("subscription_failed", symbol=deriv_ws_symbol, error=err_msg)
            raise RuntimeError(f"Subscription failed for {deriv_ws_symbol}: {err_msg}")

        sub_info = resp.get("subscription", {})
        sub_id = str(sub_info.get("id") or resp.get("tick", {}).get("id") or f"sub_{deriv_ws_symbol}")
        self._active_subscriptions[deriv_ws_symbol] = sub_id
        _log.info("subscribed_deriv_symbol", symbol=deriv_ws_symbol, sub_id=sub_id)
        return sub_id

    async def unsubscribe_symbol(self, deriv_ws_symbol: str) -> None:
        """Unsubscribe from symbol tick stream."""
        sub_id = self._active_subscriptions.pop(deriv_ws_symbol, None)
        if sub_id and self.is_connected:
            _log.info("unsubscribing_deriv_symbol", symbol=deriv_ws_symbol, sub_id=sub_id)
            try:
                await self.request({"forget": sub_id})
            except Exception as exc:
                _log.warning("unsubscribe_request_failed", error=str(exc))

    async def _message_loop(self) -> None:
        """Receive and route WebSocket messages continuously."""
        while self._is_connected and self._ws is not None:
            try:
                raw_msg = await self._ws.recv()
                msg = json.loads(raw_msg)

                # 1. Match request correlation via req_id
                req_id = msg.get("req_id")
                if isinstance(req_id, int) and req_id in self._pending_requests:
                    fut = self._pending_requests.get(req_id)
                    if fut and not fut.done():
                        fut.set_result(msg)

                # 2. Check msg_type for live tick stream
                if msg.get("msg_type") == "tick" and self.on_tick:
                    await self.on_tick(msg)

            except ConnectionClosed:
                _log.warning("websocket_connection_closed")
                self._is_connected = False
                if self.on_disconnected:
                    await self.on_disconnected()
                break
            except asyncio.CancelledError:
                break
            except Exception as exc:
                _log.warning("websocket_recv_error", error=str(exc))
                if self.on_error:
                    await self.on_error(str(exc))
