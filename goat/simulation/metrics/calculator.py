"""
Project GOAT v0.7 — Statistical Metrics Calculator

Calculates 15 descriptive statistical metrics deterministically:
1. win_rate
2. loss_rate
3. average_reward
4. average_risk
5. expected_value
6. profit_factor
7. maximum_drawdown
8. recovery_factor
9. payoff_ratio
10. trade_frequency
11. risk_adjusted_expectancy
12. simulation_consistency
13. validation_consistency
14. reproducibility_score
15. statistical_confidence

All metrics are purely descriptive and NEVER optimize future behavior or fit parameters.
"""

from __future__ import annotations

from typing import Any


class StatisticalMetricsCalculator:
    """Calculator for computing descriptive statistical simulation metrics deterministically."""

    def compute_all_metrics(self, simulated_events: list[dict[str, Any]]) -> dict[str, float]:
        """Compute 15 descriptive statistical metrics from simulated event trades.

        Args:
            simulated_events: List of event outcome dictionaries containing 'pnl' or 'return' keys.

        Returns:
            Dictionary mapping metric name to float value.
        """
        returns = []
        for ev in simulated_events:
            val = ev.get("pnl") if "pnl" in ev else ev.get("return", ev.get("profit", 0.0))
            returns.append(float(val))

        total_trades = len(returns)
        if total_trades == 0:
            return {
                "win_rate": 0.0,
                "loss_rate": 0.0,
                "average_reward": 0.0,
                "average_risk": 0.0,
                "expected_value": 0.0,
                "profit_factor": 1.0,
                "maximum_drawdown": 0.0,
                "recovery_factor": 0.0,
                "payoff_ratio": 1.0,
                "trade_frequency": 0.0,
                "risk_adjusted_expectancy": 0.0,
                "simulation_consistency": 0.0,
                "validation_consistency": 0.0,
                "reproducibility_score": 0.0,
                "statistical_confidence": 0.0,
            }

        wins = [r for r in returns if r > 0]
        losses = [r for r in returns if r < 0]

        win_rate = len(wins) / total_trades
        loss_rate = len(losses) / total_trades

        avg_reward = sum(wins) / len(wins) if wins else 0.0
        avg_risk = abs(sum(losses) / len(losses)) if losses else 0.01

        expected_value = sum(returns) / total_trades

        gross_profit = sum(wins)
        gross_loss = abs(sum(losses))
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else (gross_profit if gross_profit > 0 else 1.0)

        # Drawdown calculation
        cumulative = 0.0
        peak = 0.0
        max_dd = 0.0
        for r in returns:
            cumulative += r
            if cumulative > peak:
                peak = cumulative
            dd = peak - cumulative
            if dd > max_dd:
                max_dd = dd

        max_drawdown = min(1.0, max_dd / max(1.0, peak)) if peak > 0 else (max_dd if max_dd <= 1.0 else 1.0)
        recovery_factor = (cumulative / max_dd) if max_dd > 0 else (cumulative if cumulative > 0 else 0.0)

        payoff_ratio = (avg_reward / avg_risk) if avg_risk > 0 else 1.0
        trade_frequency = float(total_trades)

        risk_adj_expectancy = (expected_value / avg_risk) if avg_risk > 0 else expected_value
        sim_consistency = round(min(1.0, max(0.0, win_rate * 0.5 + (1.0 - max_drawdown) * 0.5)), 4)
        val_consistency = round(min(1.0, max(0.0, (profit_factor / (profit_factor + 1.0)))), 4)
        reproducibility_score = round(min(1.0, max(0.0, 1.0 - (1.0 / max(1, total_trades)))), 4)
        stat_confidence = round(min(1.0, max(0.0, total_trades / (total_trades + 10.0))), 4)

        return {
            "win_rate": round(win_rate, 4),
            "loss_rate": round(loss_rate, 4),
            "average_reward": round(avg_reward, 4),
            "average_risk": round(avg_risk, 4),
            "expected_value": round(expected_value, 4),
            "profit_factor": round(profit_factor, 4),
            "maximum_drawdown": round(max_drawdown, 4),
            "recovery_factor": round(recovery_factor, 4),
            "payoff_ratio": round(payoff_ratio, 4),
            "trade_frequency": round(trade_frequency, 4),
            "risk_adjusted_expectancy": round(risk_adj_expectancy, 4),
            "simulation_consistency": sim_consistency,
            "validation_consistency": val_consistency,
            "reproducibility_score": reproducibility_score,
            "statistical_confidence": stat_confidence,
        }
