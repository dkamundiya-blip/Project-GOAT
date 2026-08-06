"""
Project GOAT v0.8 — Deriv Session Engine

Manages Deriv WebSocket connection state lifecycle, server time synchronisation,
ping/pong heartbeat measurement, latency tracking, and reconnect attempts.
"""

from __future__ import annotations

import datetime

from goat.brokers.core.enums import ConnectionStatus
from goat.brokers.deriv.core.canonical import compute_deriv_heartbeat_id, compute_deriv_session_id
from goat.brokers.deriv.core.models import DerivHeartbeat, DerivSession


class DerivSessionEngine:
    """Engine managing Deriv protocol session lifecycle and connection telemetry."""

    def __init__(self, broker_id: str = "BRK_DERIV"):
        self.broker_id = broker_id.strip()
        self._status = ConnectionStatus.DISCONNECTED
        self._server_time: str = ""
        self._ping_ms: float = 0.0
        self._last_heartbeat: DerivHeartbeat | None = None
        self._active_session: DerivSession | None = None

    def establish_session(self, timestamp: str | None = None) -> DerivSession:
        """Establish session connection to Deriv gateway."""
        now_iso = timestamp if timestamp else datetime.datetime.now(datetime.timezone.utc).isoformat()
        self._status = ConnectionStatus.CONNECTED
        self._server_time = now_iso
        self._ping_ms = 15.0

        sess_id, canonical_hash = compute_deriv_session_id(self.broker_id, now_iso)
        self._active_session = DerivSession(
            session_id=sess_id,
            broker_id=self.broker_id,
            status=self._status,
            server_time=now_iso,
            ping_ms=self._ping_ms,
            metadata={},
            canonical_hash=canonical_hash,
        )
        return self._active_session

    def process_ping_pong(self, ping_time: str, pong_time: str, latency_ms: float = 15.0) -> DerivHeartbeat:
        """Process ping/pong heartbeat measurement."""
        self._ping_ms = max(0.0, float(latency_ms))
        if self._ping_ms > 1000.0:
            self._status = ConnectionStatus.DEGRADED

        hb_id, canonical_hash = compute_deriv_heartbeat_id(ping_time)
        self._last_heartbeat = DerivHeartbeat(
            heartbeat_id=hb_id,
            ping_timestamp=ping_time,
            pong_timestamp=pong_time,
            roundtrip_ms=self._ping_ms,
            metadata={},
            canonical_hash=canonical_hash,
        )

        time_str = self._server_time if self._server_time else ping_time
        sess_id, c_hash = compute_deriv_session_id(self.broker_id, time_str)
        self._active_session = DerivSession(
            session_id=sess_id,
            broker_id=self.broker_id,
            status=self._status,
            server_time=time_str,
            ping_ms=self._ping_ms,
            metadata={},
            canonical_hash=c_hash,
        )

        return self._last_heartbeat

    def terminate_session(self, timestamp: str | None = None) -> DerivSession:
        """Terminate Deriv gateway session."""
        now_iso = timestamp if timestamp else datetime.datetime.now(datetime.timezone.utc).isoformat()
        self._status = ConnectionStatus.DISCONNECTED
        self._server_time = now_iso

        sess_id, canonical_hash = compute_deriv_session_id(self.broker_id, now_iso)
        self._active_session = DerivSession(
            session_id=sess_id,
            broker_id=self.broker_id,
            status=self._status,
            server_time=now_iso,
            ping_ms=self._ping_ms,
            metadata={},
            canonical_hash=canonical_hash,
        )
        return self._active_session

    def get_current_session(self) -> DerivSession | None:
        """Retrieve active Deriv session telemetry."""
        return self._active_session
