"""
Project GOAT v0.7 — Deterministic Research Trend Engine

Generates deterministic research trends across research topics/domains:
- GROWING
- DECLINING
- STABLE
- CONFLICTING
- UNRESOLVED
- DORMANT
"""

from __future__ import annotations

from typing import Any

from goat.meta_analysis.core.canonical import compute_canonical_sha256, compute_trend_id
from goat.meta_analysis.core.enums import TrendDirection
from goat.meta_analysis.core.models import ResearchTrend


class TrendAnalysisEngine:
    """Engine for generating deterministic research trends across topics."""

    def analyze_trends(
        self,
        validations: list[dict[str, Any]],
        conflicts: list[dict[str, Any]],
        timestamp: str,
    ) -> list[ResearchTrend]:
        """Analyze validation runs and conflicts deterministically to generate research trends.

        Args:
            validations: List of validation run summaries.
            conflicts: List of conflict records or dicts.
            timestamp: ISO 8601 UTC timestamp string.

        Returns:
            List of ResearchTrend models sorted by trend_id.
        """
        # Group validations by topic / hypothesis_id / feature
        topic_map: dict[str, list[dict[str, Any]]] = {}
        for val in validations:
            topic = str(
                val.get("hypothesis_id")
                or val.get("feature_id")
                or val.get("topic")
                or val.get("title")
                or "GENERAL_RESEARCH"
            ).strip()
            if topic not in topic_map:
                topic_map[topic] = []
            topic_map[topic].append(val)

        trends: list[ResearchTrend] = []

        for topic in sorted(topic_map.keys()):
            val_list = topic_map[topic]
            val_ids = sorted([str(v.get("validation_id") or v.get("id")) for v in val_list])

            conf_scores = [float(v.get("confidence", 0.5)) for v in val_list]
            avg_conf = sum(conf_scores) / len(conf_scores) if conf_scores else 0.5

            statuses = [str(v.get("status") or v.get("decision")).upper() for v in val_list]
            pass_count = sum(1 for s in statuses if s in ("PASSED", "VALIDATED", "SUPPORTED"))
            fail_count = sum(1 for s in statuses if s in ("FAILED", "REJECTED", "CONTRADICTED"))

            # Check conflicts for this topic
            topic_conflicts = [
                c for c in conflicts if topic in str(c.get("validation_a")) or topic in str(c.get("validation_b")) or topic in str(c.get("explanation", ""))
            ]

            direction: TrendDirection
            strength: float
            persistence: float

            if len(topic_conflicts) > 0 or (pass_count > 0 and fail_count > 0 and abs(pass_count - fail_count) <= 1):
                direction = TrendDirection.CONFLICTING
                strength = 0.85
                persistence = 0.70
            elif avg_conf < 0.35 or (pass_count == 0 and fail_count == 0):
                direction = TrendDirection.UNRESOLVED
                strength = 0.40
                persistence = 0.30
            elif len(val_list) >= 3 and all(s in ("PASSED", "VALIDATED", "SUPPORTED") for s in statuses):
                direction = TrendDirection.GROWING
                strength = min(1.0, 0.7 + 0.1 * len(val_list))
                persistence = 0.90
            elif pass_count > fail_count:
                direction = TrendDirection.STABLE
                strength = round(avg_conf, 4)
                persistence = 0.80
            elif fail_count > pass_count:
                direction = TrendDirection.DECLINING
                strength = round(avg_conf, 4)
                persistence = 0.50
            else:
                direction = TrendDirection.DORMANT
                strength = 0.20
                persistence = 0.10

            trend_id, _ = compute_trend_id(topic, direction.value)

            payload = {
                "direction": direction.value,
                "topic": topic,
                "trend_id": trend_id,
            }
            canonical_hash = compute_canonical_sha256(payload).upper()

            trends.append(
                ResearchTrend(
                    trend_id=trend_id,
                    topic=topic,
                    direction=direction,
                    strength=round(max(0.0, min(1.0, strength)), 4),
                    persistence=round(max(0.0, min(1.0, persistence)), 4),
                    evidence=val_ids,
                    metadata={"val_count": len(val_list), "pass_count": pass_count, "fail_count": fail_count},
                    canonical_hash=canonical_hash,
                )
            )

        return sorted(trends, key=lambda t: t.trend_id)
