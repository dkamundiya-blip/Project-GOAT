"""
Project GOAT v0.9 — Research Analytics Engine
"""

import math
from typing import Any

from goat.intelligence.core.canonical import (
    compute_research_health_id,
    compute_research_trend_id,
)
from goat.intelligence.core.enums import HealthStatus, TrendDirection
from goat.intelligence.core.models import ResearchHealth, ResearchTrend


class ResearchAnalyticsEngine:
    """Quantitative Sub-Engine for Research Analytics.

    Aggregates historical research outcomes to analyze hypothesis category success rates,
    experiment design efficiency, market regime invalidations, and research time waste.
    """

    def analyze_hypothesis_success_rates(
        self,
        hypotheses_records: list[dict[str, Any]],
    ) -> dict[str, float]:
        """Compute success rate (0..1) grouped by hypothesis category."""
        category_counts: dict[str, int] = {}
        category_passes: dict[str, int] = {}

        for record in hypotheses_records:
            cat = str(record.get("category", "GENERAL")).upper()
            status = str(record.get("status", "REJECTED")).upper()

            category_counts[cat] = category_counts.get(cat, 0) + 1
            if status in ("PASSED", "PROMOTED", "VALIDATED"):
                category_passes[cat] = category_passes.get(cat, 0) + 1

        success_rates: dict[str, float] = {}
        for cat, total in category_counts.items():
            passes = category_passes.get(cat, 0)
            success_rates[cat] = round(passes / total, 4) if total > 0 else 0.0

        return success_rates

    def analyze_experiment_efficiency(
        self,
        experiment_records: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Analyze experiment efficiency, duration, and sample utility."""
        if not experiment_records:
            return {"mean_duration_seconds": 0.0, "efficiency_score": 50.0, "total_experiments": 0}

        durations = [float(e.get("duration_seconds", 300)) for e in experiment_records]
        conclusive = [e for e in experiment_records if e.get("is_conclusive", True)]

        mean_duration = sum(durations) / len(durations) if durations else 0.0
        conclusive_ratio = len(conclusive) / len(experiment_records) if experiment_records else 0.0
        efficiency_score = round(min(100.0, max(0.0, conclusive_ratio * 100.0)), 2)

        return {
            "mean_duration_seconds": round(mean_duration, 2),
            "efficiency_score": efficiency_score,
            "conclusive_experiments_count": len(conclusive),
            "total_experiments": len(experiment_records),
        }

    def analyze_regime_invalidations(
        self,
        invalidation_records: list[dict[str, Any]],
    ) -> dict[str, int]:
        """Aggregate invalidation counts by market regime."""
        regime_counts: dict[str, int] = {}
        for rec in invalidation_records:
            regime = str(rec.get("regime", "UNKNOWN")).upper()
            regime_counts[regime] = regime_counts.get(regime, 0) + 1
        return regime_counts

    def compute_research_health(
        self,
        hypotheses_records: list[dict[str, Any]],
        experiment_records: list[dict[str, Any]],
        invalidation_records: list[dict[str, Any]],
        timestamp_str: str = "2026-01-01T00:00:00Z",
    ) -> ResearchHealth:
        """Compute overall institutional research health score and diagnostic assessment."""
        success_rates = self.analyze_hypothesis_success_rates(hypotheses_records)
        exp_efficiency = self.analyze_experiment_efficiency(experiment_records)

        avg_success_rate = (
            sum(success_rates.values()) / len(success_rates) if success_rates else 0.50
        )
        eff_score = float(exp_efficiency.get("efficiency_score", 50.0))

        waste_pct = round(max(0.0, min(100.0, (1.0 - avg_success_rate) * 50.0)), 2)
        overall_score = round(min(100.0, max(0.0, (avg_success_rate * 50.0) + (eff_score * 0.50))), 2)

        if overall_score >= 80.0:
            status = HealthStatus.EXCELLENT
        elif overall_score >= 60.0:
            status = HealthStatus.GOOD
        elif overall_score >= 40.0:
            status = HealthStatus.MARGINAL
        else:
            status = HealthStatus.AT_RISK

        diagnostics = [
            f"Aggregate hypothesis success rate: {avg_success_rate:.2%}",
            f"Experiment efficiency score: {eff_score:.2f}/100",
            f"Estimated research time waste percentage: {waste_pct:.2f}%",
        ]

        h_id, h_hash = compute_research_health_id(
            status=status.value,
            health_score=overall_score,
            timestamp=timestamp_str,
        )

        return ResearchHealth(
            health_id=h_id,
            health_score=overall_score,
            status=status,
            success_rate=round(avg_success_rate, 4),
            efficiency_score=eff_score,
            waste_percentage=waste_pct,
            diagnostics=diagnostics,
            timestamp=timestamp_str,
            metadata={},
            canonical_hash=h_hash,
        )

    def compute_trend(
        self,
        metric_name: str,
        historical_values: list[float],
        timestamp_str: str = "2026-01-01T00:00:00Z",
    ) -> ResearchTrend:
        """Compute research metric trend direction and percentage change."""
        if not historical_values:
            pct_change = 0.0
            direction = TrendDirection.STABLE
        elif len(historical_values) == 1:
            pct_change = 0.0
            direction = TrendDirection.STABLE
        else:
            first = historical_values[0]
            last = historical_values[-1]
            pct_change = round(((last - first) / abs(first)) * 100.0, 2) if first != 0 else 0.0

            if pct_change > 5.0:
                direction = TrendDirection.IMPROVING
            elif pct_change < -5.0:
                direction = TrendDirection.DECLINING
            else:
                direction = TrendDirection.STABLE

        t_id, t_hash = compute_research_trend_id(
            metric_name=metric_name,
            direction=direction.value,
            timestamp=timestamp_str,
        )

        return ResearchTrend(
            trend_id=t_id,
            metric_name=metric_name,
            direction=direction,
            historical_values=list(historical_values),
            percentage_change=pct_change,
            timestamp=timestamp_str,
            metadata={},
            canonical_hash=t_hash,
        )
