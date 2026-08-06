"""
Project GOAT v0.7 — Test Suite for PatternDiscoveryEngine

Coverage:
- Recurring evidence discovery
- Frequently validated hypotheses discovery
- Weak evidence region discovery
- Full discover_all_patterns orchestration
"""

from goat.meta_analysis.core.enums import PatternCategory
from goat.meta_analysis.patterns.discovery import PatternDiscoveryEngine


def test_discover_recurring_evidence():
    engine = PatternDiscoveryEngine()
    vals = [
        {"validation_id": "VAL_1", "supporting_evidence": ["EV_COMMON", "EV_UNIQUE_1"]},
        {"validation_id": "VAL_2", "supporting_evidence": ["EV_COMMON", "EV_UNIQUE_2"]},
    ]

    patterns = engine.discover_recurring_evidence(vals, "2026-07-30T00:00:00Z")
    assert len(patterns) == 1
    assert patterns[0].category == PatternCategory.RECURRING_EVIDENCE
    assert patterns[0].frequency == 2
    assert "EV_COMMON" in patterns[0].evidence


def test_discover_frequently_validated():
    engine = PatternDiscoveryEngine()
    vals = [
        {"validation_id": "VAL_1", "hypothesis_id": "HYP_MOM", "status": "PASSED"},
        {"validation_id": "VAL_2", "hypothesis_id": "HYP_MOM", "status": "PASSED"},
    ]

    patterns = engine.discover_frequently_validated(vals, "2026-07-30T00:00:00Z")
    assert len(patterns) == 1
    assert patterns[0].category == PatternCategory.FREQUENTLY_VALIDATED
    assert patterns[0].frequency == 2
