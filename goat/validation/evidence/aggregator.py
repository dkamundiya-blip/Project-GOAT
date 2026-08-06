"""
Project GOAT v0.7 — Evidence Aggregator

Deterministic aggregation of evidence weights and confidence values
for scientific hypothesis validation.
"""

from __future__ import annotations

from typing import Any

from goat.validation.evidence.models import ValidationEvidence


class EvidenceAggregator:
    """Deterministic aggregator computing evidence summaries from collected evidence.

    No random sampling. No probabilistic simulation. Pure deterministic computation.
    """

    def aggregate_evidence(self, evidence_list: list[ValidationEvidence]) -> dict[str, Any]:
        """Aggregate a list of evidence into a deterministic summary.

        Args:
            evidence_list: List of ValidationEvidence instances.

        Returns:
            Dictionary with aggregated metrics.
        """
        if not evidence_list:
            return {
                "total_count": 0,
                "supporting_count": 0,
                "contradicting_count": 0,
                "total_weight": 0.0,
                "supporting_weight": 0.0,
                "contradicting_weight": 0.0,
                "weighted_confidence": 0.0,
                "mean_confidence": 0.0,
                "evidence_types": {},
            }

        supporting = [e for e in evidence_list if e.supports_hypothesis]
        contradicting = [e for e in evidence_list if not e.supports_hypothesis]

        total_weight = sum(e.weight for e in evidence_list)
        supporting_weight = sum(e.weight for e in supporting)
        contradicting_weight = sum(e.weight for e in contradicting)

        # Weighted confidence: sum(confidence * weight) / sum(weight)
        if total_weight > 0:
            weighted_confidence = sum(e.confidence * e.weight for e in evidence_list) / total_weight
        else:
            weighted_confidence = 0.0

        mean_confidence = sum(e.confidence for e in evidence_list) / len(evidence_list)

        # Evidence type breakdown
        type_counts: dict[str, int] = {}
        for e in evidence_list:
            type_counts[e.evidence_type] = type_counts.get(e.evidence_type, 0) + 1

        return {
            "total_count": len(evidence_list),
            "supporting_count": len(supporting),
            "contradicting_count": len(contradicting),
            "total_weight": round(total_weight, 6),
            "supporting_weight": round(supporting_weight, 6),
            "contradicting_weight": round(contradicting_weight, 6),
            "weighted_confidence": round(weighted_confidence, 6),
            "mean_confidence": round(mean_confidence, 6),
            "evidence_types": type_counts,
        }

    def compute_evidence_summary(self, evidence_list: list[ValidationEvidence]) -> dict[str, Any]:
        """Compute a complete evidence summary including per-type breakdowns.

        Args:
            evidence_list: List of ValidationEvidence instances.

        Returns:
            Dictionary with overall and per-type aggregation.
        """
        overall = self.aggregate_evidence(evidence_list)

        # Per-type breakdowns
        type_groups: dict[str, list[ValidationEvidence]] = {}
        for e in evidence_list:
            if e.evidence_type not in type_groups:
                type_groups[e.evidence_type] = []
            type_groups[e.evidence_type].append(e)

        per_type: dict[str, dict[str, Any]] = {}
        for etype, group in sorted(type_groups.items()):
            per_type[etype] = self.aggregate_evidence(group)

        return {
            "overall": overall,
            "per_type": per_type,
        }
