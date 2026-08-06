"""
Project GOAT v0.7 — Historical Replay Engine

Implements deterministic chronological event replay:
- Chronological sorting & timestamp preservation
- Deterministic event stream hashing
- Replay integrity verification & replay validation
"""

from __future__ import annotations

from typing import Any
from goat.research.edge.canonical import compute_canonical_sha256


class HistoricalReplayEngine:
    """Engine executing deterministic, chronologically ordered event replay."""

    def sort_events_chronologically(self, events: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Sort event dictionaries deterministically by timestamp then event_id or title.

        Args:
            events: List of raw event dictionaries.

        Returns:
            Sorted list of event dictionaries.
        """
        def event_key(ev: dict[str, Any]) -> tuple[str, str]:
            ts = str(ev.get("timestamp") or ev.get("time") or "").strip()
            eid = str(ev.get("event_id") or ev.get("id") or ev.get("title") or "").strip()
            return ts, eid

        return sorted(events, key=event_key)

    def compute_replay_hash(self, events: list[dict[str, Any]], seed: int = 42) -> str:
        """Compute SHA-256 digest of chronologically sorted events and seed for replay integrity verification.

        Args:
            events: List of event dictionaries.
            seed: Deterministic seed value.

        Returns:
            Full SHA-256 hex string.
        """
        sorted_evs = self.sort_events_chronologically(events)
        payload = {
            "events": sorted_evs,
            "seed": int(seed),
        }
        return compute_canonical_sha256(payload).upper()

    def verify_replay_integrity(
        self,
        events: list[dict[str, Any]],
        expected_hash: str,
        seed: int = 42,
    ) -> bool:
        """Verify that an event stream matches the expected replay hash exactly.

        Args:
            events: List of event dictionaries.
            expected_hash: Target canonical SHA-256 hash digest.
            seed: Deterministic seed value.

        Returns:
            True if replay integrity matches, False otherwise.
        """
        computed = self.compute_replay_hash(events, seed=seed)
        return computed == str(expected_hash).strip().upper()

    def replay_events(
        self,
        events: list[dict[str, Any]],
        seed: int = 42,
    ) -> tuple[list[dict[str, Any]], str]:
        """Replay event stream deterministically.

        Args:
            events: List of raw event dictionaries.
            seed: Deterministic seed value.

        Returns:
            Tuple of (sorted_replayed_events, replay_sha256_hash).
        """
        sorted_events = self.sort_events_chronologically(events)
        replay_hash = self.compute_replay_hash(sorted_events, seed=seed)
        return sorted_events, replay_hash
