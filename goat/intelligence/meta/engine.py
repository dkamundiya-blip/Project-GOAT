"""
Project GOAT v0.9 — Meta-Analysis Engine
"""

import math
from typing import Any

from goat.intelligence.core.canonical import compute_meta_analysis_id
from goat.intelligence.core.models import MetaAnalysis


class MetaAnalysisEngine:
    """Quantitative Sub-Engine for Institutional Meta-Analysis.

    Finds higher-order statistical patterns, pooled effect sizes, heterogeneity (I2),
    and edge family longevity across completed scientific studies.
    """

    def perform_meta_analysis(
        self,
        analysis_title: str,
        study_results: list[dict[str, Any]],
        timestamp_str: str = "2026-01-01T00:00:00Z",
        metadata: dict[str, Any] | None = None,
    ) -> MetaAnalysis:
        """Perform fixed/random effects meta-analysis across completed study results."""
        meta = dict(metadata or {})
        if not study_results:
            m_id, m_hash = compute_meta_analysis_id(
                analysis_title=analysis_title,
                sample_size=0,
                timestamp=timestamp_str,
            )
            return MetaAnalysis(
                meta_analysis_id=m_id,
                analysis_title=analysis_title,
                sample_size=0,
                pooled_effect_size=0.0,
                heterogeneity_i2=0.0,
                p_value=1.0,
                key_findings=["No study results provided for meta-analysis."],
                timestamp=timestamp_str,
                metadata=meta,
                canonical_hash=m_hash,
            )

        effects = [float(s.get("effect_size", 0.0)) for s in study_results]
        weights = [float(s.get("sample_size", 30)) for s in study_results]

        total_weight = sum(weights)
        if total_weight > 0:
            pooled_effect = sum(e * w for e, w in zip(effects, weights)) / total_weight
        else:
            pooled_effect = sum(effects) / len(effects)

        # Variance & Heterogeneity I2 calculation
        variances = [(e - pooled_effect) ** 2 for e in effects]
        q_stat = sum(v * w for v, w in zip(variances, weights)) if total_weight > 0 else sum(variances)

        df = max(1, len(effects) - 1)
        i2 = max(0.0, min(100.0, ((q_stat - df) / max(1e-6, q_stat)) * 100.0)) if q_stat > df else 0.0

        # Approximate p-value calculation
        z_score = abs(pooled_effect) * math.sqrt(len(effects))
        p_val = max(0.0001, min(1.0, math.exp(-0.5 * (z_score ** 2))))

        findings = [
            f"Pooled meta-analytic effect size: {pooled_effect:.4f}",
            f"Heterogeneity index I2: {i2:.2f}%",
            f"Statistical significance p-value: {p_val:.4e}",
        ]

        m_id, m_hash = compute_meta_analysis_id(
            analysis_title=analysis_title,
            sample_size=len(study_results),
            timestamp=timestamp_str,
        )

        return MetaAnalysis(
            meta_analysis_id=m_id,
            analysis_title=analysis_title,
            sample_size=len(study_results),
            pooled_effect_size=round(pooled_effect, 6),
            heterogeneity_i2=round(i2, 2),
            p_value=round(p_val, 6),
            key_findings=findings,
            timestamp=timestamp_str,
            metadata=meta,
            canonical_hash=m_hash,
        )

    def analyze_edge_family_longevity(
        self,
        edge_family: str,
        survival_records: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Compute edge family survival and longevity metrics."""
        if not survival_records:
            return {"edge_family": edge_family, "mean_longevity_days": 0.0, "survival_rate": 0.0}

        days = [float(s.get("longevity_days", 0)) for s in survival_records]
        active = [s for s in survival_records if s.get("is_active", True)]

        mean_days = sum(days) / len(days) if days else 0.0
        survival_rate = len(active) / len(survival_records) if survival_records else 0.0

        return {
            "edge_family": edge_family,
            "mean_longevity_days": round(mean_days, 2),
            "survival_rate": round(survival_rate, 4),
            "total_edges": len(survival_records),
            "active_edges": len(active),
        }
