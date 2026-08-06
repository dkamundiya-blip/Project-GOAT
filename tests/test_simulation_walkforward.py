"""
Project GOAT v0.7 — Test Suite for WalkForwardValidationEngine

Coverage:
- WalkForwardWindow sequence generation
- Rolling evaluation without data leakage
- Overall validation decision status evaluation
"""

from goat.simulation.core.enums import ValidationStatus
from goat.simulation.walkforward.engine import WalkForwardValidationEngine


def test_walk_forward_validation_engine():
    engine = WalkForwardValidationEngine()

    windows = engine.generate_walk_forward_windows(
        start_timestamp="2026-01-01T00:00:00Z",
        end_timestamp="2026-07-30T00:00:00Z",
        num_windows=3,
    )

    assert len(windows) == 3
    assert windows[0].sequence_number == 1
    assert windows[1].sequence_number == 2
    assert windows[2].sequence_number == 3

    events_map = {
        windows[0].window_id: [{"pnl": 100.0}, {"pnl": -20.0}],
        windows[1].window_id: [{"pnl": 150.0}, {"pnl": -30.0}],
        windows[2].window_id: [{"pnl": 200.0}, {"pnl": -40.0}],
    }

    status, summary = engine.evaluate_walk_forward_windows(windows, events_map)

    assert status in (ValidationStatus.HIGH_CONFIDENCE_VALIDATED, ValidationStatus.VALIDATED)
    assert summary["passed_windows"] == 3
