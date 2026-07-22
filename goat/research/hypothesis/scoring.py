"""
Project GOAT v0.4 — EdgeScore & Evidence Discipline Engine

Calculates transparent, bounded EdgeScore (0-100) representing research evidence quality.
Enforces metric-specific effect magnitude normalization, saturating q-value evidence,
and weak practical effect threshold classification.
"""

from __future__ import annotations

import numpy as np

from goat.logging import get_logger

_log = get_logger("hypothesis.scoring")


def normalize_effect_magnitude(
    effect_size: float,
    method: str = "cohens_d",
    baseline_std: float = 1.0,
) -> float:
    """Normalize effect size deterministically according to its specific metric scale.

    Returns:
        Bounded score contribution from 0.0 to 25.0 points.
    """
    abs_eff = abs(effect_size)

    if method in ("cohens_d", "standardized_mean_diff"):
        # Benchmark: d = 0.8 is "large" -> 25.0 pts
        norm = (abs_eff / 0.8) * 25.0

    elif method == "rank_biserial":
        # Benchmark: r = 0.5 is "large" correlation -> 25.0 pts
        norm = (abs_eff / 0.5) * 25.0

    elif method in ("relative_risk", "odds_ratio"):
        # Benchmark: log(RR) = log(2.0) approx 0.693 -> 25.0 pts
        log_rr = abs(np.log(max(abs_eff, 1e-6)))
        norm = (log_rr / np.log(2.0)) * 25.0

    elif method in ("mean_diff", "median_diff"):
        # Scale relative to baseline standard deviation
        rel_diff = abs_eff / max(baseline_std, 1e-6)
        norm = (rel_diff / 0.8) * 25.0

    elif method == "prop_diff":
        # Benchmark: delta_p = 0.20 -> 25.0 pts
        norm = (abs_eff / 0.20) * 25.0

    else:
        norm = (abs_eff / 0.5) * 25.0

    return float(np.clip(norm, 0.0, 25.0))


def is_practically_weak_effect(
    effect_size: float,
    method: str = "cohens_d",
    baseline_std: float = 1.0,
) -> bool:
    """Evaluate whether an effect size falls below practical minimum thresholds."""
    abs_eff = abs(effect_size)

    if method in ("cohens_d", "standardized_mean_diff"):
        return abs_eff < 0.10

    elif method == "rank_biserial":
        return abs_eff < 0.05

    elif method in ("relative_risk", "odds_ratio"):
        return abs(np.log(max(abs_eff, 1e-6))) < np.log(1.10)

    elif method in ("mean_diff", "median_diff"):
        return (abs_eff / max(baseline_std, 1e-6)) < 0.10

    elif method == "prop_diff":
        return abs_eff < 0.02

    return abs_eff < 0.05


def calculate_edge_score(
    effect_size: float,
    q_value: float,
    effect_method: str = "cohens_d",
    baseline_std: float = 1.0,
    train_effect_size: float | None = None,
    val_effect_size: float | None = None,
    walk_forward_agreement_pct: float = 1.0,
    sample_size: int = 100,
    min_sample_size: int = 100,
    dependence_overlap_risk: bool = False,
) -> dict[str, float]:
    """Compute transparent, bounded EdgeScore (0-100) representing research evidence quality.

    CRITICAL DISCLAIMER:
    --------------------
    EdgeScore represents RESEARCH EVIDENCE QUALITY ONLY.
    It does NOT represent probability of winning, expected return, or trading profitability.

    Returns:
        Dict of component scores and total ``edge_score``.
    """
    # 1. Metric-specific effect magnitude score (0-25 pts)
    s_mag = normalize_effect_magnitude(effect_size, method=effect_method, baseline_std=baseline_std)

    # 2. Bounded / Saturating statistical evidence score (0-25 pts)
    # Saturates at q <= 0.001 (-log10(q) >= 3.0)
    q_clamped = max(q_value, 1e-15)
    neg_log_q = -float(np.log10(q_clamped))
    s_stat = float(np.clip((neg_log_q / 3.0) * 25.0, 0.0, 25.0))

    # 3. Validation stability score (0-25 pts)
    if train_effect_size is not None and val_effect_size is not None:
        if np.sign(train_effect_size) == np.sign(val_effect_size) and abs(train_effect_size) > 0:
            ratio = abs(val_effect_size) / abs(train_effect_size)
            s_val = float(np.clip(ratio * 25.0, 0.0, 25.0))
        else:
            s_val = 0.0
    else:
        s_val = 12.5  # Neutral default for unvalidated exploratory stage

    # 4. Temporal consistency score (0-15 pts)
    s_temp = float(np.clip(walk_forward_agreement_pct * 15.0, 0.0, 15.0))

    # 5. Sample sufficiency score (0-10 pts)
    s_suff = float(np.clip((sample_size / max(min_sample_size, 1)) * 10.0, 0.0, 10.0))

    # 6. Dependence embargo penalty (-15 to 0 pts)
    p_dep = -15.0 if dependence_overlap_risk else 0.0

    total_score = float(np.clip(s_mag + s_stat + s_val + s_temp + s_suff + p_dep, 0.0, 100.0))

    return {
        "total_edge_score": round(total_score, 2),
        "effect_magnitude_score": round(s_mag, 2),
        "statistical_confidence_score": round(s_stat, 2),
        "validation_stability_score": round(s_val, 2),
        "temporal_consistency_score": round(s_temp, 2),
        "sample_sufficiency_score": round(s_suff, 2),
        "dependence_penalty": round(p_dep, 2),
    }
