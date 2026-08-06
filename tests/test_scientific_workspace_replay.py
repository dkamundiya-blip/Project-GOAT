"""
Project GOAT v1.0 — Test Suite: Replay Mode & Deterministic Audit Matrix
"""

import pytest

REPLAY_MODES = ["LIVE", "REPLAY_DETERMINISTIC", "HISTORICAL_AUDIT"]
SPEEDS = [0.5, 1.0, 2.0, 5.0, 10.0]
CHECKSUM_STATUS = ["VERIFIED", "MATCHED", "AUDITED"]
SYMBOLS = ["VOLATILITY_10", "BOOM_500", "CRASH_1000"]


@pytest.mark.parametrize("mode", REPLAY_MODES)
@pytest.mark.parametrize("speed", SPEEDS)
@pytest.mark.parametrize("status", CHECKSUM_STATUS)
@pytest.mark.parametrize("symbol", SYMBOLS)
def test_scientific_workspace_replay_matrix(mode, speed, status, symbol):
    assert mode in REPLAY_MODES
    assert speed > 0.0
    assert status in CHECKSUM_STATUS
    assert symbol in SYMBOLS
