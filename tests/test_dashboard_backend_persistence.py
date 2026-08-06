"""
Project GOAT v1.0 — Test Suite: Dashboard Backend Persistence Read-Only Adapter
"""

import pytest

from goat.dashboard.persistence.sqlite import DashboardReadOnlyRepositoryAdapter

LIMITS = [1, 5, 10, 20, 50, 100]


@pytest.mark.parametrize("limit", LIMITS)
def test_dashboard_persistence_matrix(limit):
    adapter = DashboardReadOnlyRepositoryAdapter()
    summary = adapter.get_dashboard_summary_metrics()
    assert summary["database_status"] == "ONLINE_READ_ONLY"
    assert summary["hypothesis_count"] == 42

    hypotheses = adapter.get_active_hypotheses(limit=limit)
    assert len(hypotheses) > 0

    decisions = adapter.get_governance_decisions(limit=limit)
    assert len(decisions) > 0

    symbols = adapter.get_market_symbols_status()
    assert len(symbols) == 12
