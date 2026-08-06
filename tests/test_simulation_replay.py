"""
Project GOAT v0.7 — Test Suite for HistoricalReplayEngine

Coverage:
- Chronological event sorting and timestamp preservation
- Deterministic event stream hashing
- Replay integrity verification and validation
"""

from goat.simulation.replay.engine import HistoricalReplayEngine


def test_historical_replay_sorting_and_hashing():
    engine = HistoricalReplayEngine()

    raw_events = [
        {"timestamp": "2026-01-03T00:00:00Z", "event_id": "EV_3", "pnl": 100.0},
        {"timestamp": "2026-01-01T00:00:00Z", "event_id": "EV_1", "pnl": 50.0},
        {"timestamp": "2026-01-02T00:00:00Z", "event_id": "EV_2", "pnl": -20.0},
    ]

    replayed_events, replay_hash = engine.replay_events(raw_events, seed=42)

    assert len(replayed_events) == 3
    assert replayed_events[0]["event_id"] == "EV_1"
    assert replayed_events[1]["event_id"] == "EV_2"
    assert replayed_events[2]["event_id"] == "EV_3"

    assert engine.verify_replay_integrity(raw_events, replay_hash, seed=42)
    assert not engine.verify_replay_integrity(raw_events, "INVALID_HASH", seed=42)
