"""
Project GOAT v0.8 — Broker Session Engine

Manages connection lifecycle state, heartbeat freshness, reconnect tracking,
latency metrics, and session telemetry without broker-specific implementation details.
"""

from __future__ import annotations

import datetime

from goat.brokers.core.canonical import compute_connection_id
from goat.brokers.core.enums import ConnectionStatus
from goat.brokers.core.models import BrokerConnection


class BrokerSessionEngine:
    """Engine responsible for tracking broker session connection states and telemetry."""

    def __init__(self, broker_id: str):
        self.broker_id = broker_id.strip()
        self._current_status = ConnectionStatus.DISCONNECTED
        self._connected_at: str | None = None
        self._disconnected_at: str | None = None
        self._last_heartbeat: str | None = None
        self._latency_ms: float = 0.0
        self._reconnect_attempts: int = 0
        self._active_connection: BrokerConnection | None = None

    def establish_session(self, timestamp: str | None = None) -> BrokerConnection:
        """Establish a new broker connection session."""
        now_iso = timestamp if timestamp else datetime.datetime.now(datetime.timezone.utc).isoformat()
        self._current_status = ConnectionStatus.CONNECTED
        self._connected_at = now_iso
        self._disconnected_at = None
        self._last_heartbeat = now_iso
        self._latency_ms = 10.0

        conn_id, canonical_hash = compute_connection_id(self.broker_id, now_iso)
        self._active_connection = BrokerConnection(
            connection_id=conn_id,
            broker_id=self.broker_id,
            status=self._current_status,
            connected_at=now_iso,
            disconnected_at=None,
            heartbeat_timestamp=now_iso,
            latency_ms=self._latency_ms,
            reconnect_attempts=self._reconnect_attempts,
            metadata={},
            canonical_hash=canonical_hash,
        )
        return self._active_connection

    def record_heartbeat(self, latency_ms: float = 10.0, timestamp: str | None = None) -> BrokerConnection:
        """Record session heartbeat telemetry."""
        now_iso = timestamp if timestamp else datetime.datetime.now(datetime.timezone.utc).isoformat()
        self._last_heartbeat = now_iso
        self._latency_ms = float(latency_ms)

        if self._latency_ms > 1000.0:
            self._current_status = ConnectionStatus.DEGRADED

        if not self._connected_at:
            self._connected_at = now_iso

        conn_id, canonical_hash = compute_connection_id(self.broker_id, self._connected_at)
        self._active_connection = BrokerConnection(
            connection_id=conn_id,
            broker_id=self.broker_id,
            status=self._current_status,
            connected_at=self._connected_at,
            disconnected_at=self._disconnected_at,
            heartbeat_timestamp=now_iso,
            latency_ms=self._latency_ms,
            reconnect_attempts=self._reconnect_attempts,
            metadata={},
            canonical_hash=canonical_hash,
        )
        return self._active_connection

    def trigger_reconnect(self, timestamp: str | None = None) -> BrokerConnection:
        """Trigger reconnection tracking."""
        now_iso = timestamp if timestamp else datetime.datetime.now(datetime.timezone.utc).isoformat()
        self._current_status = ConnectionStatus.RECONNECTING
        self._reconnect_attempts += 1

        if not self._connected_at:
            self._connected_at = now_iso

        conn_id, canonical_hash = compute_connection_id(self.broker_id, self._connected_at)
        self._active_connection = BrokerConnection(
            connection_id=conn_id,
            broker_id=self.broker_id,
            status=self._current_status,
            connected_at=self._connected_at,
            disconnected_at=self._disconnected_at,
            heartbeat_timestamp=self._last_heartbeat if self._last_heartbeat else now_iso,
            latency_ms=self._latency_ms,
            reconnect_attempts=self._reconnect_attempts,
            metadata={},
            canonical_hash=canonical_hash,
        )
        return self._active_connection

    def terminate_session(self, timestamp: str | None = None) -> BrokerConnection:
        """Terminate active broker connection session."""
        now_iso = timestamp if timestamp else datetime.datetime.now(datetime.timezone.utc).isoformat()
        self._current_status = ConnectionStatus.DISCONNECTED
        self._disconnected_at = now_iso

        if not self._connected_at:
            self._connected_at = now_iso

        conn_id, canonical_hash = compute_connection_id(self.broker_id, self._connected_at)
        self._active_connection = BrokerConnection(
            connection_id=conn_id,
            broker_id=self.broker_id,
            status=self._current_status,
            connected_at=self._connected_at,
            disconnected_at=self._disconnected_at,
            heartbeat_timestamp=self._last_heartbeat if self._last_heartbeat else now_iso,
            latency_ms=self._latency_ms,
            reconnect_attempts=self._reconnect_attempts,
            metadata={},
            canonical_hash=canonical_hash,
        )
        return self._active_connection

    def get_current_connection(self) -> BrokerConnection | None:
        """Retrieve current connection telemetry."""
        return self._active_connection
