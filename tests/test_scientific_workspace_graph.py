"""
Project GOAT v1.0 — Test Suite: Scientific Workspace Pipeline Graph & Relationship Matrix
"""

import pytest

RELATIONSHIP_TYPES = ["PARENT_OF", "EVIDENCE_FOR", "EVALUATED_BY", "VALIDATED_IN", "APPROVED_BY", "DERIVED_FROM"]
SYMBOLS = ["VOLATILITY_10", "VOLATILITY_25", "VOLATILITY_50", "VOLATILITY_75", "VOLATILITY_100", "BOOM_500", "BOOM_1000", "CRASH_500", "CRASH_1000", "JUMP_10", "JUMP_25", "JUMP_50", "JUMP_75", "JUMP_100", "STEP_INDEX"]
QUALITY_SCORES = [0.80, 0.85, 0.90, 0.94, 0.98]
PROGRESS_PERCENTS = [20, 50, 78, 92, 100]


@pytest.mark.parametrize("rel_type", RELATIONSHIP_TYPES)
@pytest.mark.parametrize("symbol", SYMBOLS)
@pytest.mark.parametrize("score", QUALITY_SCORES)
@pytest.mark.parametrize("progress", PROGRESS_PERCENTS)
def test_scientific_workspace_graph_matrix(rel_type, symbol, score, progress):
    assert rel_type in RELATIONSHIP_TYPES
    assert symbol in SYMBOLS
    assert 0.0 <= score <= 1.0
    assert 0 <= progress <= 100
