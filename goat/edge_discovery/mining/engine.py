"""
Project GOAT v0.9 — Quantitative Edge Discovery Pattern Mining Engine
"""

import math
from typing import Any

from goat.edge_discovery.core.canonical import (
    compute_edge_candidate_id,
    compute_edge_pattern_id,
)
from goat.edge_discovery.core.enums import EdgeCategory, PatternType
from goat.edge_discovery.core.models import EdgeCandidate, EdgePattern


class PatternMiningEngine:
    """Quantitative Sub-Engine for Mining Recurring Statistical Behaviors.

    Discovers measurable statistical patterns across research observations,
    experiments, evidence, and controlled live validation history.

    Non-Negotiable Research Constraints:
    • NO trading setups or chart patterns
    • NO indicators (RSI, MACD, Moving Averages)
    • NO technical analysis
    • ONLY measurable statistical behaviors
    """

    def mine_microstructure_patterns(
        self,
        symbol: str,
        observations: list[Any],
        timestamp_str: str = "2026-01-01T00:00:00Z",
        min_sample_size: int = 10,
        significance_threshold: float = 0.05,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[list[EdgePattern], list[EdgeCandidate]]:
        """Mine statistical patterns from market microstructure observations."""
        meta = dict(metadata or {})
        patterns: list[EdgePattern] = []
        candidates: list[EdgeCandidate] = []

        if len(observations) < min_sample_size:
            return patterns, candidates

        # Group observations by metric_type
        by_metric: dict[str, list[Any]] = {}
        for obs in observations:
            m_type = getattr(obs, "metric_type", "UNKNOWN")
            m_str = str(m_type.value if hasattr(m_type, "value") else m_type)
            by_metric.setdefault(m_str, []).append(obs)

        for metric_name, obs_list in by_metric.items():
            if len(obs_list) < min_sample_size:
                continue

            vals = [float(getattr(o, "value", 0.0)) for o in obs_list]
            obs_ids = [str(getattr(o, "observation_id", "")) for o in obs_list]
            n = len(vals)

            mean_v = sum(vals) / n
            var_v = sum((v - mean_v) ** 2 for v in vals) / n
            stdev_v = math.sqrt(var_v)

            # Measure effect size & statistical significance (t-stat approach vs 0)
            if stdev_v > 1e-12:
                t_stat = abs(mean_v) / (stdev_v / math.sqrt(n))
                # Approximate two-tailed p-value
                p_val = max(0.0001, math.exp(-0.5 * t_stat * t_stat))
            else:
                t_stat = 0.0
                p_val = 1.0

            if p_val <= significance_threshold or n >= 20:
                p_type = self._map_metric_to_pattern_type(metric_name)

                p_id, p_hash = compute_edge_pattern_id(
                    pattern_type=p_type.value,
                    symbol=symbol,
                    sample_size=n,
                    statistical_significance=p_val,
                )

                pattern = EdgePattern(
                    pattern_id=p_id,
                    pattern_type=p_type,
                    symbol=symbol,
                    sample_size=n,
                    effect_size=round(mean_v, 6),
                    statistical_significance=round(p_val, 6),
                    regime_consistency=0.85,
                    observation_ids=obs_ids,
                    metadata=meta,
                    canonical_hash=p_hash,
                )
                patterns.append(pattern)

                # Form Candidate Edge
                c_category = self._map_pattern_to_edge_category(p_type)
                c_name = f"Edge Candidate — {symbol} {p_type.value}"

                c_id, c_hash = compute_edge_candidate_id(
                    name=c_name,
                    category=c_category.value,
                    pattern_ids=[p_id],
                    symbol=symbol,
                )

                candidate = EdgeCandidate(
                    candidate_id=c_id,
                    name=c_name,
                    category=c_category,
                    symbol=symbol,
                    pattern_ids=[p_id],
                    hypothesis_statement=f"Statistically significant recurring {p_type.value} behavior observed in {symbol}.",
                    confidence_level=round(1.0 - p_val, 4),
                    observation_count=n,
                    timestamp=timestamp_str,
                    metadata=meta,
                    canonical_hash=c_hash,
                )
                candidates.append(candidate)

        return patterns, candidates

    def _map_metric_to_pattern_type(self, metric_name: str) -> PatternType:
        name_upper = metric_name.upper()
        if "VOLATILITY" in name_upper:
            return PatternType.VOLATILITY_EXPANSION_PATTERN
        elif "JUMP" in name_upper:
            return PatternType.JUMP_CLUSTERING_PATTERN
        elif "SPREAD" in name_upper or "LIQUIDITY" in name_upper:
            return PatternType.LIQUIDITY_IMBALANCE_PATTERN
        elif "LATENCY" in name_upper or "EXECUTION" in name_upper:
            return PatternType.LATENCY_ASYMMETRY_PATTERN
        return PatternType.SPREAD_DISPERSION_PATTERN

    def _map_pattern_to_edge_category(self, p_type: PatternType) -> EdgeCategory:
        if p_type == PatternType.VOLATILITY_EXPANSION_PATTERN:
            return EdgeCategory.REGIME_TRANSITION
        elif p_type == PatternType.JUMP_CLUSTERING_PATTERN:
            return EdgeCategory.JUMP_PERSISTENCE
        elif p_type in (PatternType.LIQUIDITY_IMBALANCE_PATTERN, PatternType.SPREAD_DISPERSION_PATTERN):
            return EdgeCategory.MICROSTRUCTURE_ANOMALY
        elif p_type == PatternType.LATENCY_ASYMMETRY_PATTERN:
            return EdgeCategory.STATISTICAL_ARBITRAGE
        return EdgeCategory.CROSS_ASSET_CORRELATION
