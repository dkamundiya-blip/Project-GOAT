"""
Project GOAT Phase 6 — Historical Evaluation Engine (`goat.edge_discovery.evaluator`)

Evaluates hypotheses against historical feature vectors and computes 16 quantitative performance metrics.
"""

from __future__ import annotations

import math
from typing import Sequence

from goat.edge_discovery.models.edge import EdgePerformanceMetrics
from goat.edge_discovery.models.hypothesis import ResearchHypothesis
from goat.feature_engineering.models.feature_vector import FeatureVector


class HistoricalEvaluationEngine:
    """Quantitative Historical Evaluation Engine evaluating candidate hypotheses over historical observations."""

    def evaluate_hypothesis(
        self,
        hypothesis: ResearchHypothesis,
        feature_vectors: Sequence[FeatureVector],
        forward_returns: Sequence[float],
    ) -> EdgePerformanceMetrics:
        """Evaluate a hypothesis on historical feature vectors and forward returns.

        Returns:
            EdgePerformanceMetrics containing 16 quantitative metrics.
        """
        if len(feature_vectors) != len(forward_returns):
            raise ValueError("feature_vectors and forward_returns must have equal length")

        matched_returns: list[float] = []

        for idx, fv in enumerate(feature_vectors):
            # Check if all hypothesis conditions match
            match = True
            for cond in hypothesis.conditions:
                f_val = fv.get_feature(cond.feature_name, default=0.0)
                if not cond.evaluate(f_val):
                    match = False
                    break

            if match:
                ret = forward_returns[idx] * hypothesis.prediction.direction
                matched_returns.append(ret)

        sample_size = len(matched_returns)
        if sample_size == 0:
            return EdgePerformanceMetrics(
                sample_size=0,
                win_rate=0.0,
                loss_rate=0.0,
                expected_value=0.0,
                average_return=0.0,
                median_return=0.0,
                max_gain=0.0,
                max_loss=0.0,
                profit_factor=0.0,
                sharpe_ratio=0.0,
                sortino_ratio=0.0,
                calmar_ratio=0.0,
                max_drawdown=0.0,
                recovery_factor=0.0,
                trade_frequency=0.0,
                holding_period=float(hypothesis.prediction.horizon_bars),
            )

        wins = [r for r in matched_returns if r > 0]
        losses = [r for r in matched_returns if r < 0]

        win_rate = len(wins) / sample_size
        loss_rate = len(losses) / sample_size

        gross_profit = sum(wins)
        gross_loss = abs(sum(losses))
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else (999.0 if gross_profit > 0 else 1.0)

        avg_return = sum(matched_returns) / sample_size
        sorted_rets = sorted(matched_returns)
        median_return = sorted_rets[sample_size // 2]

        max_gain = max(matched_returns)
        max_loss = min(matched_returns)

        # Expected Value
        expected_value = avg_return

        # Variance & Standard Deviations
        var_r = sum((r - avg_return) ** 2 for r in matched_returns) / sample_size if sample_size > 1 else 0.0
        std_r = math.sqrt(var_r)

        # Downside Deviation for Sortino Ratio
        downside_sq = sum(r ** 2 for r in matched_returns if r < 0)
        downside_std = math.sqrt(downside_sq / sample_size) if sample_size > 0 else 1e-6

        # Sharpe & Sortino Ratios (Annualized assuming 252 days)
        sharpe_ratio = (avg_return / max(std_r, 1e-6)) * math.sqrt(252)
        sortino_ratio = (avg_return / max(downside_std, 1e-6)) * math.sqrt(252)

        # Maximum Drawdown (Peak to Trough on cumulative returns)
        cum_equity = 1.0
        peak = 1.0
        max_dd = 0.0
        for r in matched_returns:
            cum_equity *= (1.0 + r)
            if cum_equity > peak:
                peak = cum_equity
            dd = (peak - cum_equity) / peak
            if dd > max_dd:
                max_dd = dd

        # Calmar Ratio & Recovery Factor
        net_profit = cum_equity - 1.0
        calmar_ratio = (avg_return * 252) / max(max_dd, 1e-6)
        recovery_factor = net_profit / max(max_dd, 1e-6)

        # Trade Frequency (trades per day estimated)
        trade_freq = sample_size / max(len(feature_vectors) / 1440.0, 1.0)

        return EdgePerformanceMetrics(
            sample_size=sample_size,
            win_rate=round(win_rate, 4),
            loss_rate=round(loss_rate, 4),
            expected_value=round(expected_value, 6),
            average_return=round(avg_return, 6),
            median_return=round(median_return, 6),
            max_gain=round(max_gain, 6),
            max_loss=round(max_loss, 6),
            profit_factor=round(profit_factor, 4),
            sharpe_ratio=round(sharpe_ratio, 4),
            sortino_ratio=round(sortino_ratio, 4),
            calmar_ratio=round(calmar_ratio, 4),
            max_drawdown=round(max_dd, 4),
            recovery_factor=round(recovery_factor, 4),
            trade_frequency=round(trade_freq, 4),
            holding_period=float(hypothesis.prediction.horizon_bars),
        )
