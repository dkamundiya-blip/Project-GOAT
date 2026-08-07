"""
Project GOAT Phase 6 — Market Regime Validator (`goat.edge_discovery.regime`)

Evaluates quantitative edge performance separately across market regimes, sessions, symbols, and timeframes.
"""

from __future__ import annotations

from typing import Sequence

from goat.edge_discovery.evaluator.engine import HistoricalEvaluationEngine
from goat.edge_discovery.models.hypothesis import ResearchHypothesis
from goat.feature_engineering.models.feature_vector import FeatureVector


class MarketRegimeValidator:
    """Quantitative Market Regime Validator evaluating edge robustness across distinct market environments."""

    def __init__(self, evaluation_engine: HistoricalEvaluationEngine | None = None):
        self.evaluation_engine = evaluation_engine or HistoricalEvaluationEngine()

    def evaluate_regimes(
        self,
        hypothesis: ResearchHypothesis,
        feature_vectors: Sequence[FeatureVector],
        forward_returns: Sequence[float],
    ) -> dict[str, dict[str, float]]:
        """Evaluate edge metrics partitioned by market regimes.

        Returns:
            Nested dictionary mapping regime category -> performance metrics breakdown.
        """
        regime_subsets: dict[str, tuple[list[FeatureVector], list[float]]] = {
            "BULL_TREND": ([], []),
            "BEAR_TREND": ([], []),
            "SIDEWAYS": ([], []),
            "HIGH_VOLATILITY": ([], []),
            "LOW_VOLATILITY": ([], []),
        }

        for fv, ret in zip(feature_vectors, forward_returns):
            trend_dir = fv.get_feature("trend_direction", default=0.0)
            vol_regime = fv.get_feature("volatility_regime", default=0.5)

            if trend_dir > 0:
                regime_subsets["BULL_TREND"][0].append(fv)
                regime_subsets["BULL_TREND"][1].append(ret)
            elif trend_dir < 0:
                regime_subsets["BEAR_TREND"][0].append(fv)
                regime_subsets["BEAR_TREND"][1].append(ret)
            else:
                regime_subsets["SIDEWAYS"][0].append(fv)
                regime_subsets["SIDEWAYS"][1].append(ret)

            if vol_regime >= 1.0:
                regime_subsets["HIGH_VOLATILITY"][0].append(fv)
                regime_subsets["HIGH_VOLATILITY"][1].append(ret)
            elif vol_regime <= 0.0:
                regime_subsets["LOW_VOLATILITY"][0].append(fv)
                regime_subsets["LOW_VOLATILITY"][1].append(ret)

        results: dict[str, dict[str, float]] = {}

        for regime_name, (fvs, rets) in regime_subsets.items():
            if len(fvs) > 0:
                m = self.evaluation_engine.evaluate_hypothesis(hypothesis, fvs, rets)
                results[regime_name] = {
                    "sample_size": float(m.sample_size),
                    "win_rate": m.win_rate,
                    "expected_value": m.expected_value,
                    "sharpe_ratio": m.sharpe_ratio,
                    "max_drawdown": m.max_drawdown,
                }
            else:
                results[regime_name] = {
                    "sample_size": 0.0,
                    "win_rate": 0.0,
                    "expected_value": 0.0,
                    "sharpe_ratio": 0.0,
                    "max_drawdown": 0.0,
                }

        return results
