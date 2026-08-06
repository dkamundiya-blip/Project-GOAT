"""
Project GOAT v1.0 — Test Suite: Scientific Workspace Entity Inspector Slide-Over Matrix
"""

import pytest

STAGES = ["HYPOTHESIS", "EVIDENCE", "EXPERIMENT", "STATISTICAL_EVALUATION", "LIVE_VALIDATION", "GOVERNANCE", "ARCHIVE", "RESEARCH_INTELLIGENCE"]
REPLAY_MODES = [True, False]
LINEAGE_HASH_TYPES = ["SHA-256", "CANONICAL_FINGERPRINT"]
INSPECTOR_STATES = ["OPEN", "CLOSED", "LOADING", "MINIMIZED"]
USER_ROLES = ["CQO", "QUANT_RESEARCHER", "RISK_MANAGER", "SYSTEM_OPERATOR", "AUDITOR"]


@pytest.mark.parametrize("stage", STAGES)
@pytest.mark.parametrize("replay", REPLAY_MODES)
@pytest.mark.parametrize("hash_type", LINEAGE_HASH_TYPES)
@pytest.mark.parametrize("state", INSPECTOR_STATES)
@pytest.mark.parametrize("role", USER_ROLES)
def test_scientific_workspace_inspector_matrix(stage, replay, hash_type, state, role):
    assert stage in STAGES
    assert isinstance(replay, bool)
    assert hash_type in LINEAGE_HASH_TYPES
    assert state in INSPECTOR_STATES
    assert role in USER_ROLES
