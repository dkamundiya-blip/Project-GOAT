"""
Project GOAT Phase 7 — Natural Language Explanation Layer (`goat.ai_reasoning.explanation`)

Translates quantitative research outputs and evidence into human-readable explanations across 3 target levels:
BEGINNER, INTERMEDIATE, and PROFESSIONAL_QUANT.
"""

from __future__ import annotations

from goat.ai_reasoning.models.report import ExplanationLevel, ResearchReport
from goat.edge_discovery.models.edge import DiscoveredEdge


class NaturalLanguageExplanationLayer:
    """Translates empirical quantitative outputs into persona-tailored research explanations."""

    def explain_edge(
        self,
        edge: DiscoveredEdge,
        level: ExplanationLevel = ExplanationLevel.PROFESSIONAL_QUANT,
    ) -> dict[str, str | float]:
        """Explain a DiscoveredEdge for a specific persona level."""
        m = edge.metrics

        if level == ExplanationLevel.BEGINNER:
            summary = (
                f"This trading pattern ({', '.join(edge.feature_combination)}) has shown a consistent winning record "
                f"of {m.win_rate:.0%} over {m.sample_size} past market tests on {', '.join(edge.supported_symbols)}. "
                f"On average, it generates a small positive gain per test with a low risk of big losses."
            )
            risk = f"Risk Warning: The maximum price drop seen in past tests was {m.max_drawdown:.1%}."

        elif level == ExplanationLevel.INTERMEDIATE:
            summary = (
                f"Edge {edge.edge_id} on {', '.join(edge.supported_symbols)} ({', '.join(edge.supported_timeframes)}) "
                f"has an Expected Return of {m.expected_value:.4%} per trade with a Win Rate of {m.win_rate:.1%}. "
                f"The Sharpe Ratio is {m.sharpe_ratio:.2f} and the Profit Factor is {m.profit_factor:.2f} across {m.sample_size} samples."
            )
            risk = f"Drawdown Risk: Max Peak-to-Trough Drawdown is {m.max_drawdown:.2%}, Recovery Factor is {m.recovery_factor:.2f}."

        else:  # PROFESSIONAL_QUANT
            summary = (
                f"DiscoveredEdge {edge.edge_id} [Features: {', '.join(edge.feature_combination)}] "
                f"demonstrates statistically significant positive expectancy (EV = {m.expected_value:.6f}, "
                f"Sharpe = {m.sharpe_ratio:.4f}, Sortino = {m.sortino_ratio:.4f}, Calmar = {m.calmar_ratio:.4f}) "
                f"over N = {m.sample_size} observations. Null hypothesis rejected at p-value = {edge.p_value:.6f} "
                f"(Cohen's d = {edge.effect_size:.4f}, 95% CI [{edge.confidence_interval_low:.6f}, {edge.confidence_interval_high:.6f}]). "
                f"Composite Score = {edge.composite_score:.4f}."
            )
            risk = (
                f"Quantitative Risk Profile: MaxDD = {m.max_drawdown:.4f}, Recovery Factor = {m.recovery_factor:.4f}, "
                f"Walk-Forward OOS DegRatio = {edge.walk_forward_metrics.get('degradation_ratio', 1.0):.4f}."
            )

        return {
            "edge_id": edge.edge_id,
            "explanation_level": level.value,
            "summary_explanation": summary,
            "risk_explanation": risk,
            "composite_score": edge.composite_score,
        }

    def explain_report(self, report: ResearchReport) -> str:
        """Render a formatted string representation of a ResearchReport according to its explanation level."""
        lines = [
            f"=== {report.title} ===",
            f"Level: {report.explanation_level.value} | Generated: {report.timestamp}",
            "",
            "--- EXECUTIVE SUMMARY ---",
            report.executive_summary,
            "",
            "--- DETERMINISTIC CONCLUSIONS ---",
        ]
        for c in report.conclusions:
            lines.append(f"• Verdict: [{c.status_verdict}] {c.claim}")
            for step in c.reasoning_steps:
                lines.append(f"    - {step}")

        lines.extend(["", "--- SUPPORTING STATISTICS ---"])
        for k, v in report.supporting_statistics.items():
            lines.append(f"  {k}: {v}")

        lines.extend(["", "--- RISK FACTORS ---"])
        for r in report.risk_factors:
            lines.append(f"  ! {r}")

        lines.extend(["", "--- RECOMMENDED NEXT STEPS ---"])
        for ns in report.recommended_next_steps:
            lines.append(f"  -> {ns}")

        return "\n".join(lines)
