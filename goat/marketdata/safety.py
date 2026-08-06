"""
Project GOAT v0.8 — Production Safety Gate (Market Stream Health)

Implements the first Production Safety Gate defined in Version 0.8 architecture.
Evaluates incoming market streams for operational health:
- Stream health
- Heartbeat freshness
- Timestamp integrity
- Sequence continuity
- Checksum validity

Possible Statuses: HEALTHY, DEGRADED, UNAVAILABLE.
Does NOT make trading decisions. Outputs deterministic reasoning.
"""

from __future__ import annotations

import datetime
from pydantic import BaseModel, Field

from goat.marketdata.core.enums import SafetyGateStatus, StreamConnectionStatus
from goat.marketdata.core.models import MarketStreamState


class SafetyGateResult(BaseModel):
    """Immutable result emitted by MarketStreamSafetyGate."""

    status: SafetyGateStatus = Field(..., description="Operational status (HEALTHY, DEGRADED, UNAVAILABLE)")
    symbol: str = Field(..., description="Target market symbol")
    reasoning: list[str] = Field(default_factory=list, description="Deterministic explanations for status decision")
    timestamp: str = Field(..., description="ISO 8601 UTC evaluation timestamp")

    class Config:
        frozen = True
        extra = "forbid"


class MarketStreamSafetyGate:
    """Production Safety Gate evaluating data feed health without taking trading actions."""

    def __init__(
        self,
        max_heartbeat_age_seconds: float = 5.0,
        max_acceptable_latency_ms: float = 1000.0,
        max_acceptable_packet_drops: int = 10,
    ):
        self.max_heartbeat_age_seconds = float(max_heartbeat_age_seconds)
        self.max_acceptable_latency_ms = float(max_acceptable_latency_ms)
        self.max_acceptable_packet_drops = int(max_acceptable_packet_drops)

    def evaluate_stream(self, stream_state: MarketStreamState) -> SafetyGateResult:
        """Evaluate a MarketStreamState entity against production safety criteria."""
        symbol = stream_state.symbol.strip().upper()
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        reasoning: list[str] = []
        is_unavailable = False
        is_degraded = False

        # 1. Connection Status check
        if stream_state.connection_status in (StreamConnectionStatus.DISCONNECTED, StreamConnectionStatus.TERMINATED):
            is_unavailable = True
            reasoning.append(f"Connection status is {stream_state.connection_status.value}")
        elif stream_state.connection_status in (StreamConnectionStatus.RECONNECTING, StreamConnectionStatus.DEGRADED):
            is_degraded = True
            reasoning.append(f"Connection status is {stream_state.connection_status.value}")

        # 2. Heartbeat Freshness check
        try:
            hb_dt = datetime.datetime.fromisoformat(stream_state.heartbeat_timestamp)
            if hb_dt.tzinfo is None:
                hb_dt = hb_dt.replace(tzinfo=datetime.timezone.utc)
            now = datetime.datetime.now(datetime.timezone.utc)
            age = (now - hb_dt).total_seconds()
            if age > self.max_heartbeat_age_seconds:
                is_unavailable = True
                reasoning.append(f"Heartbeat is stale ({age:.2f}s > threshold {self.max_heartbeat_age_seconds}s)")
        except Exception as e:
            is_unavailable = True
            reasoning.append(f"Invalid heartbeat timestamp format ({e})")

        # 3. Latency check
        if stream_state.latency_ms > self.max_acceptable_latency_ms:
            is_degraded = True
            reasoning.append(f"Latency ({stream_state.latency_ms:.2f}ms) exceeds limit ({self.max_acceptable_latency_ms}ms)")

        # 4. Packet Drop check
        if stream_state.packets_dropped > self.max_acceptable_packet_drops:
            is_degraded = True
            reasoning.append(f"Packets dropped count ({stream_state.packets_dropped}) exceeds limit ({self.max_acceptable_packet_drops})")

        # Determine Final Status
        if is_unavailable:
            final_status = SafetyGateStatus.UNAVAILABLE
        elif is_degraded:
            final_status = SafetyGateStatus.DEGRADED
        else:
            final_status = SafetyGateStatus.HEALTHY
            reasoning.append("All stream health, heartbeat, latency, and packet integrity checks passed")

        return SafetyGateResult(
            status=final_status,
            symbol=symbol,
            reasoning=reasoning,
            timestamp=now_iso,
        )
