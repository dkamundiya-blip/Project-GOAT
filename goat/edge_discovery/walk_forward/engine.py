"""
Project GOAT Phase 6 — Walk-Forward Validation (`goat.edge_discovery.walk_forward`)

Splits historical observations into rolling Train, Validation, and Out-of-Sample (OOS) windows to prevent look-ahead bias.
"""

from __future__ import annotations

from typing import Sequence

from goat.edge_discovery.evaluator.engine import HistoricalEvaluationEngine
from goat.edge_discovery.models.hypothesis import ResearchHypothesis
from goat.feature_engineering.models.feature_vector import FeatureVector


class WalkForwardValidator:
    """Quantitative Walk-Forward Validator executing rolling in-sample vs out-of-sample edge verification."""

    def __init__(
        self,
        evaluation_engine: HistoricalEvaluationEngine | None = None,
        train_ratio: float = 0.6,
        val_ratio: float = 0.2,
    ):
        self.evaluation_engine = evaluation_engine or HistoricalEvaluationEngine()
        self.train_ratio = train_ratio
        self.val_ratio = val_ratio

    def validate_walk_forward(
        self,
        hypothesis: ResearchHypothesis,
        feature_vectors: Sequence[FeatureVector],
        forward_returns: Sequence[float],
    ) -> dict[str, float]:
        """Perform 3-way walk-forward validation (Train / Validation / Out-of-Sample).

        Returns:
            Dictionary containing train_sharpe, val_sharpe, oos_sharpe, oos_win_rate, degradation_ratio, passed_oos.
        """
        n = len(feature_vectors)
        if n < 20:
            return {
                "train_sharpe": 0.0,
                "val_sharpe": 0.0,
                "oos_sharpe": 0.0,
                "oos_win_rate": 0.0,
                "oos_expected_value": 0.0,
                "degradation_ratio": 1.0,
                "passed_oos": 0.0,
            }

        idx_train = int(n * self.train_ratio)
        idx_val = int(n * (self.train_ratio + self.val_ratio))

        # 1. Train Window
        train_fvs = feature_vectors[:idx_train]
        train_rets = forward_returns[:idx_train]
        m_train = self.evaluation_engine.evaluate_hypothesis(hypothesis, train_fvs, train_rets)

        # 2. Validation Window
        val_fvs = feature_vectors[idx_train:idx_val]
        val_rets = forward_returns[idx_train:idx_val]
        m_val = self.evaluation_engine.evaluate_hypothesis(hypothesis, val_fvs, val_rets)

        # 3. Out-of-Sample (OOS) Window
        oos_fvs = feature_vectors[idx_val:]
        oos_rets = forward_returns[idx_val:]
        m_oos = self.evaluation_engine.evaluate_hypothesis(hypothesis, oos_fvs, oos_rets)

        # Calculate performance degradation ratio (OOS EV / Train EV)
        if abs(m_train.expected_value) > 1e-8:
            degradation = m_oos.expected_value / m_train.expected_value
        else:
            degradation = 0.0

        passed = 1.0 if (m_oos.expected_value > 0 and m_oos.sample_size >= 3 and degradation >= 0.5) else 0.0

        return {
            "train_sharpe": m_train.sharpe_ratio,
            "val_sharpe": m_val.sharpe_ratio,
            "oos_sharpe": m_oos.sharpe_ratio,
            "oos_win_rate": m_oos.win_rate,
            "oos_expected_value": m_oos.expected_value,
            "degradation_ratio": round(degradation, 4),
            "passed_oos": passed,
        }
