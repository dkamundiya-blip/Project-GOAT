"""
Project GOAT v0.8 — Market Stream Engine

Tracks real-time feed state, heartbeat freshness, packet counts, packet drops,
reconnect counters, latency metrics, and connection health status per symbol.
"""

from __future__ import annotations

import datetime
from goat.marketdata.core.canonical import compute_stream_id
from goat.marketdata.core.enums import StreamConnectionStatus
from goat.marketdata.core.models import MarketStreamState
from goat.research.edge.canonical import compute_canonical_sha256


class MarketStreamEngine:
    """Engine responsible for maintaining active stream health state and metrics per symbol."""

    def __init__(self, broker: str = "DERIV", heartbeat_timeout_seconds: float = 5.0):
        self.broker = broker.strip().upper()
        self.heartbeat_timeout_seconds = float(heartbeat_timeout_seconds)
        self._states: dict[str, MarketStreamState] = {}

    def get_or_create_stream_state(self, symbol: str) -> MarketStreamState:
        """Get or initialize MarketStreamState for a symbol."""
        sym = symbol.strip().upper()
        if sym not in self._states:
            now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
            stream_id, canonical_hash = compute_stream_id(
                broker=self.broker,
                symbol=sym,
                heartbeat_timestamp=now_iso,
            )
            checksum = compute_canonical_sha256(
                {
                    "broker": self.broker,
                    "heartbeat_timestamp": now_iso,
                    "symbol": sym,
                }
            )
            self._states[sym] = MarketStreamState(
                stream_id=stream_id,
                broker=self.broker,
                symbol=sym,
                connection_status=StreamConnectionStatus.CONNECTED,
                heartbeat_timestamp=now_iso,
                latency_ms=0.0,
                packets_received=0,
                packets_dropped=0,
                reconnect_count=0,
                metadata={},
                canonical_hash=canonical_hash,
            )
        return self._states[sym]

    def record_packet_received(
        self,
        symbol: str,
        latency_ms: float = 0.0,
        timestamp: str | None = None,
    ) -> MarketStreamState:
        """Record successful packet reception and update state."""
        state = self.get_or_create_stream_state(symbol)
        ts = timestamp if timestamp else datetime.datetime.now(datetime.timezone.utc).isoformat()

        stream_id, canonical_hash = compute_stream_id(
            broker=self.broker,
            symbol=state.symbol,
            heartbeat_timestamp=ts,
        )

        status = StreamConnectionStatus.CONNECTED
        if latency_ms > 2000.0:
            status = StreamConnectionStatus.DEGRADED

        updated_state = MarketStreamState(
            stream_id=stream_id,
            broker=self.broker,
            symbol=state.symbol,
            connection_status=status,
            heartbeat_timestamp=ts,
            latency_ms=round(float(latency_ms), 3),
            packets_received=state.packets_received + 1,
            packets_dropped=state.packets_dropped,
            reconnect_count=state.reconnect_count,
            metadata=state.metadata,
            canonical_hash=canonical_hash,
        )
        self._states[state.symbol] = updated_state
        return updated_state

    def record_packet_dropped(self, symbol: str, reason: str = "MALFORMED") -> MarketStreamState:
        """Record a dropped or malformed packet."""
        state = self.get_or_create_stream_state(symbol)
        ts = datetime.datetime.now(datetime.timezone.utc).isoformat()

        stream_id, canonical_hash = compute_stream_id(
            broker=self.broker,
            symbol=state.symbol,
            heartbeat_timestamp=ts,
        )

        meta = dict(state.metadata)
        meta["last_drop_reason"] = reason

        updated_state = MarketStreamState(
            stream_id=stream_id,
            broker=self.broker,
            symbol=state.symbol,
            connection_status=state.connection_status,
            heartbeat_timestamp=ts,
            latency_ms=state.latency_ms,
            packets_received=state.packets_received,
            packets_dropped=state.packets_dropped + 1,
            reconnect_count=state.reconnect_count,
            metadata=meta,
            canonical_hash=canonical_hash,
        )
        self._states[state.symbol] = updated_state
        return updated_state

    def record_reconnect(self, symbol: str) -> MarketStreamState:
        """Record stream reconnection event."""
        state = self.get_or_create_stream_state(symbol)
        ts = datetime.datetime.now(datetime.timezone.utc).isoformat()

        stream_id, canonical_hash = compute_stream_id(
            broker=self.broker,
            symbol=state.symbol,
            heartbeat_timestamp=ts,
        )

        updated_state = MarketStreamState(
            stream_id=stream_id,
            broker=self.broker,
            symbol=state.symbol,
            connection_status=StreamConnectionStatus.RECONNECTING,
            heartbeat_timestamp=ts,
            latency_ms=state.latency_ms,
            packets_received=state.packets_received,
            packets_dropped=state.packets_dropped,
            reconnect_count=state.reconnect_count + 1,
            metadata=state.metadata,
            canonical_hash=canonical_hash,
        )
        self._states[state.symbol] = updated_state
        return updated_state

    def update_connection_status(
        self, symbol: str, status: StreamConnectionStatus
    ) -> MarketStreamState:
        """Explicitly set connection status."""
        state = self.get_or_create_stream_state(symbol)
        ts = datetime.datetime.now(datetime.timezone.utc).isoformat()

        stream_id, canonical_hash = compute_stream_id(
            broker=self.broker,
            symbol=state.symbol,
            heartbeat_timestamp=ts,
        )

        updated_state = MarketStreamState(
            stream_id=stream_id,
            broker=self.broker,
            symbol=state.symbol,
            connection_status=status,
            heartbeat_timestamp=ts,
            latency_ms=state.latency_ms,
            packets_received=state.packets_received,
            packets_dropped=state.packets_dropped,
            reconnect_count=state.reconnect_count,
            metadata=state.metadata,
            canonical_hash=canonical_hash,
        )
        self._states[state.symbol] = updated_state
        return updated_state

    def evaluate_stream_health(self, symbol: str) -> StreamConnectionStatus:
        """Evaluate current connection health based on heartbeat timestamp age."""
        state = self.get_or_create_stream_state(symbol)
        try:
            hb_dt = datetime.datetime.fromisoformat(state.heartbeat_timestamp)
            if hb_dt.tzinfo is None:
                hb_dt = hb_dt.replace(tzinfo=datetime.timezone.utc)
            now = datetime.datetime.now(datetime.timezone.utc)
            age_seconds = (now - hb_dt).total_seconds()
            if age_seconds > self.heartbeat_timeout_seconds:
                return StreamConnectionStatus.DISCONNECTED
        except Exception:
            return StreamConnectionStatus.DISCONNECTED

        return state.connection_status
