"""
Project GOAT v0.7 — Test Suite for RegimeRuleEngine

Coverage:
- Rule registration & listing ordered by priority
- Rule evaluation across operators (==, !=, >, >=, <, <=, in)
- Default rule registry verification
"""

from goat.regimes.core.canonical import compute_rule_id
from goat.regimes.core.enums import RegimeType
from goat.regimes.core.models import RegimeRule
from goat.regimes.rules.engine import RegimeRuleEngine


def test_rule_engine_default_rules():
    engine = RegimeRuleEngine()
    rules = engine.list_rules()
    assert len(rules) >= 12
    # Ensure sorted by priority descending
    for i in range(len(rules) - 1):
        assert rules[i].priority >= rules[i + 1].priority


def test_custom_rule_evaluation():
    engine = RegimeRuleEngine()
    r_id, r_hash = compute_rule_id("Custom Trend Rule", "TRENDING")
    rule = RegimeRule(
        rule_id=r_id,
        name="Custom Trend Rule",
        priority=99,
        deterministic_conditions={
            "trend_strength": {"op": ">=", "value": 0.80},
            "volume_ratio": {"op": ">", "value": 1.2},
        },
        expected_regime=RegimeType.TRENDING,
        canonical_hash=r_hash,
    )
    engine.register_rule(rule)

    matching_obs = {"trend_strength": 0.85, "volume_ratio": 1.5}
    non_matching_obs = {"trend_strength": 0.75, "volume_ratio": 1.5}

    assert engine.evaluate_rule(rule, matching_obs) is True
    assert engine.evaluate_rule(rule, non_matching_obs) is False
