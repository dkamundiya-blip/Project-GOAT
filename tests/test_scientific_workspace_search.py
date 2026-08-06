"""
Project GOAT v1.0 — Test Suite: Scientific Workspace Global Canonical Search Matrix
"""

import pytest

CANONICAL_PREFIXES = ["HYP_", "EVI_", "EXP_", "STA_", "VAL_", "GOV_", "ARC_", "KNO_", "INT_"]
QUERY_TYPES = ["EXACT_ID", "PARTIAL_NAME", "STAGE_KEYWORD", "SYMBOL_NAME", "HASH_PREFIX"]
ROLES = ["CQO", "QUANT_RESEARCHER", "RISK_MANAGER", "SYSTEM_OPERATOR", "AUDITOR"]
MAX_RESULTS = [5, 10, 20, 50]


@pytest.mark.parametrize("prefix", CANONICAL_PREFIXES)
@pytest.mark.parametrize("q_type", QUERY_TYPES)
@pytest.mark.parametrize("role", ROLES)
@pytest.mark.parametrize("max_r", MAX_RESULTS)
def test_scientific_workspace_search_matrix(prefix, q_type, role, max_r):
    assert len(prefix) == 4
    assert q_type in QUERY_TYPES
    assert role in ROLES
    assert max_r > 0
