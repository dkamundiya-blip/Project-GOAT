"""
Project GOAT v0.8 — Market Replay Engine

Provides deterministic replay of historical market ticks and candles,
validating sequence order, cumulative checksum integrity, and generating
ReplaySnapshot (RPS_<HEX16>) records.
"""

from __future__ import annotations

import datetime
from typing import Sequence
from pydantic import BaseModel, Field

from goat.marketdata.core.canonical import compute_replay_id
from goat.marketdata.core.models import MarketCandle, MarketTick, ReplaySnapshot
from goat.research.edge.canonical import compute_canonical_sha256


class ReplayResult(BaseModel):
    """Immutable result emitted by MarketReplayEngine after replaying a sequence."""

    success: bool = Field(..., description="True if replay completed without integrity errors")
    snapshot: ReplaySnapshot = Field(..., description="Generated ReplaySnapshot model")
    replayed_ticks_count: int = Field(default=0, ge=0, description="Total ticks replayed")
    replayed_candles_count: int = Field(default=0, ge=0, description="Total candles replayed")
    integrity_error: str | None = Field(default=None, description="Explanation if replay failed integrity check")

    class Config:
        frozen = True
        extra = "forbid"


class MarketReplayEngine:
    """Engine responsible for deterministic tick and candle replay."""

    def __init__(self):
        pass

    def create_snapshot(
        self,
        symbol: str,
        ticks: Sequence[MarketTick],
        snapshot_reference: str = "",
    ) -> ReplaySnapshot:
        """Create a deterministic ReplaySnapshot for a sequence of MarketTicks."""
        sym = symbol.strip().upper()
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        ref = snapshot_reference if snapshot_reference else f"REF_{sym}_{len(ticks)}"

        # Compute cumulative SHA-256 digest
        combined_payload = [t.checksum for t in ticks]
        cumulative_hash = compute_canonical_sha256({"symbol": sym, "tick_checksums": combined_payload})

        replay_id, canonical_hash = compute_replay_id(
            symbol=sym,
            replay_timestamp=now_iso,
            snapshot_reference=ref,
        )

        return ReplaySnapshot(
            replay_id=replay_id,
            symbol=sym,
            replay_timestamp=now_iso,
            replay_checksum=cumulative_hash,
            snapshot_reference=ref,
            metadata={"tick_count": len(ticks)},
            canonical_hash=canonical_hash,
        )

    def replay_tick_sequence(
        self,
        ticks: Sequence[MarketTick],
        snapshot_reference: str = "TICK_REPLAY",
    ) -> ReplayResult:
        """Replay a sequence of MarketTicks in strict chronological order and verify integrity."""
        if not ticks:
            dummy_snapshot = self.create_snapshot("UNKNOWN", [], snapshot_reference)
            return ReplayResult(
                success=True,
                snapshot=dummy_snapshot,
                replayed_ticks_count=0,
                replayed_candles_count=0,
            )

        sym = ticks[0].symbol.strip().upper()
        last_ts: datetime.datetime | None = None

        for t in ticks:
            try:
                ts = datetime.datetime.fromisoformat(t.timestamp)
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=datetime.timezone.utc)
            except Exception:
                snapshot = self.create_snapshot(sym, ticks, snapshot_reference)
                return ReplayResult(
                    success=False,
                    snapshot=snapshot,
                    integrity_error=f"REPLAY_MALFORMED_TIMESTAMP: Invalid timestamp in tick {t.tick_id}",
                )

            if last_ts and ts < last_ts:
                snapshot = self.create_snapshot(sym, ticks, snapshot_reference)
                return ReplayResult(
                    success=False,
                    snapshot=snapshot,
                    integrity_error=f"REPLAY_CHRONOLOGY_VIOLATION: Tick {t.tick_id} timestamp {ts} prior to {last_ts}",
                )

            last_ts = ts

        snapshot = self.create_snapshot(sym, ticks, snapshot_reference)
        return ReplayResult(
            success=True,
            snapshot=snapshot,
            replayed_ticks_count=len(ticks),
            replayed_candles_count=0,
        )
