"""
Project GOAT v0.7 — Deterministic Regime Rule Engine

Provides rule evaluation across market observations and maintains default rule registries for all 12 regime types:
- TRENDING
- RANGING
- BREAKOUT
- REVERSAL
- ACCUMULATION
- DISTRIBUTION
- HIGH_VOLATILITY
- LOW_VOLATILITY
- LIQUIDITY_EXPANSION
- LIQUIDITY_CONTRACTION
- TRANSITIONAL
- UNDEFINED
"""

from __future__ import annotations

from typing import Any

from goat.regimes.core.canonical import compute_canonical_sha256, compute_rule_id
from goat.regimes.core.enums import RegimeType
from goat.regimes.core.models import RegimeRule


class RegimeRuleEngine:
    """Engine for evaluating deterministic conditions against market observation metrics."""

    def __init__(self) -> None:
        self._rules: dict[str, RegimeRule] = {}
        self._load_default_rules()

    def register_rule(self, rule: RegimeRule) -> None:
        """Register a custom RegimeRule."""
        self._rules[rule.rule_id] = rule

    def get_rule(self, rule_id: str) -> RegimeRule | None:
        """Fetch rule by ID."""
        return self._rules.get(rule_id)

    def list_rules(self) -> list[RegimeRule]:
        """Return all rules ordered deterministically by priority (descending) then rule_id."""
        rules = list(self._rules.values())
        return sorted(rules, key=lambda r: (-r.priority, r.rule_id))

    def evaluate_rule(self, rule: RegimeRule, observations: dict[str, Any]) -> bool:
        """Evaluate whether market observations satisfy all deterministic conditions of a rule.

        Args:
            rule: Target RegimeRule.
            observations: Dict of current market metrics.

        Returns:
            True if all conditions match, False otherwise.
        """
        conds = rule.deterministic_conditions
        if not conds:
            return False

        for metric, condition in sorted(conds.items()):
            if metric not in observations:
                return False
            actual_val = observations[metric]

            if isinstance(condition, dict):
                op = str(condition.get("op", "==")).strip()
                target_val = condition.get("value")

                if op == "==" and actual_val != target_val:
                    return False
                elif op == "!=" and actual_val == target_val:
                    return False
                elif op == ">" and not (float(actual_val) > float(target_val)):
                    return False
                elif op == ">=" and not (float(actual_val) >= float(target_val)):
                    return False
                elif op == "<" and not (float(actual_val) < float(target_val)):
                    return False
                elif op == "<=" and not (float(actual_val) <= float(target_val)):
                    return False
                elif op == "in" and isinstance(target_val, list) and actual_val not in target_val:
                    return False
            else:
                if actual_val != condition:
                    return False

        return True

    def evaluate_all_rules(
        self, observations: dict[str, Any]
    ) -> list[tuple[RegimeRule, bool]]:
        """Evaluate all registered rules against observations deterministically."""
        sorted_rules = self.list_rules()
        results: list[tuple[RegimeRule, bool]] = []
        for r in sorted_rules:
            matched = self.evaluate_rule(r, observations)
            results.append((r, matched))
        return results

    def _load_default_rules(self) -> None:
        """Initialize default rule set for 12 supported regimes."""
        default_rule_specs = [
            ("Rule Trending", "High directional trend strength", 90, {"trend_strength": {"op": ">=", "value": 0.70}}, RegimeType.TRENDING),
            ("Rule Ranging", "Low trend strength and mean-reverting structure", 80, {"trend_strength": {"op": "<", "value": 0.35}}, RegimeType.RANGING),
            ("Rule Breakout", "High volume and volatility expansion with structural breakout", 95, {"breakout_flag": {"op": "==", "value": True}}, RegimeType.BREAKOUT),
            ("Rule Reversal", "Decelerating momentum and extreme price location", 85, {"momentum_state": {"op": "==", "value": "DECELERATING"}, "trend_strength": {"op": ">=", "value": 0.60}}, RegimeType.REVERSAL),
            ("Rule High Volatility", "Volatility z-score exceeding high threshold", 90, {"volatility_zscore": {"op": ">=", "value": 1.5}}, RegimeType.HIGH_VOLATILITY),
            ("Rule Low Volatility", "Volatility z-score below low threshold", 75, {"volatility_zscore": {"op": "<=", "value": -1.0}}, RegimeType.LOW_VOLATILITY),
            ("Rule Liquidity Expansion", "Volume ratio expanding", 80, {"volume_ratio": {"op": ">=", "value": 1.4}}, RegimeType.LIQUIDITY_EXPANSION),
            ("Rule Liquidity Contraction", "Volume ratio contracting", 70, {"volume_ratio": {"op": "<=", "value": 0.6}}, RegimeType.LIQUIDITY_CONTRACTION),
            ("Rule Accumulation", "Low volatility consolidation with institutional buying", 75, {"structural_state": {"op": "==", "value": "CONSOLIDATION"}, "participation_state": {"op": "==", "value": "INSTITUTIONAL"}}, RegimeType.ACCUMULATION),
            ("Rule Distribution", "High volatility consolidation with institutional selling", 75, {"structural_state": {"op": "==", "value": "CONSOLIDATION"}, "participation_state": {"op": "==", "value": "RETAIL"}}, RegimeType.DISTRIBUTION),
            ("Rule Transitional", "Mixed indicators across trend and volatility", 50, {"transition_flag": {"op": "==", "value": True}}, RegimeType.TRANSITIONAL),
            ("Rule Undefined", "Default fallback rule", 1, {"undefined_flag": {"op": "==", "value": True}}, RegimeType.UNDEFINED),
        ]

        for name, desc, priority, conds, expected in default_rule_specs:
            r_id, r_hash = compute_rule_id(name, expected.value)
            rule = RegimeRule(
                rule_id=r_id,
                name=name,
                description=desc,
                priority=priority,
                deterministic_conditions=conds,
                expected_regime=expected,
                canonical_hash=r_hash,
            )
            self._rules[rule.rule_id] = rule
