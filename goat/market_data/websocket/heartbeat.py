"""
Project GOAT v1.0 — WebSocket Heartbeat Monitor

Monitors connection freshness and triggers heartbeat failure events upon ping timeouts.
"""

from __future__ import annotations

import asyncio
import datetime
from typing import Callable, Coroutine, Any
from goat.logging import get_logger

_log = get_logger("websocket.heartbeat")


class HeartbeatMonitor:
    """Monitors WebSocket connection health via periodic ping requests."""

    def __init__(
        self,
        ping_interval_seconds: float = 20.0,
        timeout_seconds: float = 10.0,
    ):
        self.ping_interval_seconds = ping_interval_seconds
        self.timeout_seconds = timeout_seconds
        self._last_pong_time: datetime.datetime | None = None
        self._task: asyncio.Task[None] | None = None
        self._running = False
        self._ping_fn: Callable[[], Coroutine[Any, Any, bool]] | None = None
        self._on_timeout_fn: Callable[[], Coroutine[Any, Any, None]] | None = None

    def start(
        self,
        ping_fn: Callable[[], Coroutine[Any, Any, bool]],
        on_timeout_fn: Callable[[], Coroutine[Any, Any, None]],
    ) -> None:
        """Start the async heartbeat monitoring loop."""
        self._ping_fn = ping_fn
        self._on_timeout_fn = on_timeout_fn
        self._running = True
        self._last_pong_time = datetime.datetime.now(datetime.timezone.utc)
        self._task = asyncio.create_task(self._loop())
        _log.info("heartbeat_monitor_started", interval=self.ping_interval_seconds)

    def record_pong(self) -> None:
        """Record successful pong / heartbeat response."""
        self._last_pong_time = datetime.datetime.now(datetime.timezone.utc)

    async def stop(self) -> None:
        """Stop heartbeat monitoring loop."""
        self._running = False
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except (asyncio.CancelledError, Exception):
                pass
        _log.info("heartbeat_monitor_stopped")

    async def _loop(self) -> None:
        """Continuous ping heartbeat loop."""
        while self._running:
            try:
                await asyncio.sleep(self.ping_interval_seconds)
                if not self._running or not self._ping_fn:
                    break

                # Send ping
                success = await self._ping_fn()
                if success:
                    self.record_pong()
                else:
                    _log.warning("heartbeat_ping_failed")
                    if self._on_timeout_fn:
                        await self._on_timeout_fn()
                    break

                # Check freshness
                if self._last_pong_time:
                    age = (datetime.datetime.now(datetime.timezone.utc) - self._last_pong_time).total_seconds()
                    if age > (self.ping_interval_seconds + self.timeout_seconds):
                        _log.error("heartbeat_timeout_exceeded", age_seconds=round(age, 1))
                        if self._on_timeout_fn:
                            await self._on_timeout_fn()
                        break

            except asyncio.CancelledError:
                break
            except Exception as exc:
                _log.error("heartbeat_error", error=str(exc))
                if self._on_timeout_fn:
                    await self._on_timeout_fn()
                break
