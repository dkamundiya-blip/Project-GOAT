"""
Project GOAT v0.8 — Market Gap Detection Engine

Detects sequence number discontinuities, timestamp jumps, stream interruptions,
and heartbeat timeouts, generating deterministic MarketGap (MGP_<HEX16>) records.
"""

from __future__ import annotations

import datetime
from goat.marketdata.core.canonical import compute_gap_id
from goat.marketdata.core.enums import GapReason
from goat.marketdata.core.models import MarketGap, MarketTick
from goat.research.edge.canonical import compute_canonical_sha256


class MarketGapDetectionEngine:
    """Engine responsible for inspecting tick sequences and streams to detect data gaps."""

    def __init__(self, max_allowed_time_gap_seconds: float = 10.0):
        self.max_allowed_time_gap_seconds = float(max_allowed_time_gap_seconds)
        self._last_tick: dict[str, MarketTick] = {}

    def reset_state(self, symbol: str | None = None) -> None:
        """Reset internal sequence tracking."""
        if symbol:
            self._last_tick.pop(symbol.strip().upper(), None)
        else:
            self._last_tick.clear()

    def check_tick(self, tick: MarketTick) -> MarketGap | None:
        """Inspect a new MarketTick against the last seen tick for the symbol.

        Returns:
            MarketGap model if a sequence or timestamp gap is detected, else None.
        """
        sym = tick.symbol.strip().upper()

        if sym not in self._last_tick:
            self._last_tick[sym] = tick
            return None

        last_tick = self._last_tick[sym]
        gap_detected = False
        reason = GapReason.SEQUENCE_DISCONTINUITY
        missing_packets = 1

        # 1. Sequence Gap Check
        expected_seq = last_tick.sequence_number + 1
        if tick.sequence_number > expected_seq:
            gap_detected = True
            missing_packets = tick.sequence_number - expected_seq
            reason = GapReason.SEQUENCE_DISCONTINUITY

        # 2. Timestamp Jump Check
        try:
            current_ts = datetime.datetime.fromisoformat(tick.timestamp)
            last_ts = datetime.datetime.fromisoformat(last_tick.timestamp)
            if current_ts.tzinfo is None:
                current_ts = current_ts.replace(tzinfo=datetime.timezone.utc)
            if last_ts.tzinfo is None:
                last_ts = last_ts.replace(tzinfo=datetime.timezone.utc)

            elapsed_seconds = (current_ts - last_ts).total_seconds()
            if elapsed_seconds > self.max_allowed_time_gap_seconds:
                gap_detected = True
                reason = GapReason.TIMESTAMP_JUMP
                if missing_packets == 1 and elapsed_seconds > 0:
                    missing_packets = max(1, int(elapsed_seconds))
        except Exception:
            pass

        self._last_tick[sym] = tick

        if gap_detected:
            gap_id, canonical_hash = compute_gap_id(
                symbol=sym,
                start_timestamp=last_tick.timestamp,
                end_timestamp=tick.timestamp,
                reason=reason.value,
            )

            checksum = compute_canonical_sha256(
                {
                    "end_timestamp": tick.timestamp,
                    "missing_packets": missing_packets,
                    "reason": reason.value,
                    "start_timestamp": last_tick.timestamp,
                    "symbol": sym,
                }
            )

            return MarketGap(
                gap_id=gap_id,
                symbol=sym,
                start_timestamp=last_tick.timestamp,
                end_timestamp=tick.timestamp,
                missing_packets=missing_packets,
                reason=reason,
                metadata={
                    "last_sequence_number": last_tick.sequence_number,
                    "current_sequence_number": tick.sequence_number,
                },
                canonical_hash=canonical_hash,
            )

        return None

    def create_connection_gap(
        self,
        symbol: str,
        start_timestamp: str,
        end_timestamp: str,
        reason: GapReason = GapReason.CONNECTION_LOST,
        missing_packets: int = 1,
    ) -> MarketGap:
        """Explicitly generate a connection interruption MarketGap record."""
        sym = symbol.strip().upper()

        gap_id, canonical_hash = compute_gap_id(
            symbol=sym,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            reason=reason.value,
        )

        checksum = compute_canonical_sha256(
            {
                "end_timestamp": end_timestamp,
                "missing_packets": missing_packets,
                "reason": reason.value,
                "start_timestamp": start_timestamp,
                "symbol": sym,
            }
        )

        return MarketGap(
            gap_id=gap_id,
            symbol=sym,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            missing_packets=missing_packets,
            reason=reason,
            metadata={"explicit_gap": True},
            canonical_hash=canonical_hash,
        )
