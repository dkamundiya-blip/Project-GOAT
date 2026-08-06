"""
Project GOAT v0.7 — Deterministic Pattern Discovery Engine

Implements rule-based pattern discovery across accumulated scientific evidence:
- Recurring evidence
- Recurring relationships
- Frequently validated findings
- Long-term reproducibility
- Stable scientific observations
- Scientific anomalies
- Weak evidence regions
- Emerging research domains
"""

from __future__ import annotations

from typing import Any

from goat.integration.core.models import KnowledgeEdge, KnowledgeNode
from goat.meta_analysis.core.canonical import compute_canonical_sha256, compute_pattern_id
from goat.meta_analysis.core.enums import PatternCategory
from goat.meta_analysis.core.models import ResearchCluster, ResearchPattern


class PatternDiscoveryEngine:
    """Engine for rule-based deterministic discovery of scientific research patterns."""

    def discover_recurring_evidence(
        self, validations: list[dict[str, Any]], timestamp: str
    ) -> list[ResearchPattern]:
        """Discover evidence artifacts referenced across multiple validation runs."""
        ev_counts: dict[str, list[str]] = {}
        for val in validations:
            val_id = str(val.get("validation_id") or val.get("id") or "")
            ev_list = val.get("supporting_evidence") or [val_id]
            for ev in ev_list:
                ev_str = str(ev).strip()
                if ev_str not in ev_counts:
                    ev_counts[ev_str] = []
                if val_id not in ev_counts[ev_str]:
                    ev_counts[ev_str].append(val_id)

        patterns: list[ResearchPattern] = []
        for ev, val_list in sorted(ev_counts.items()):
            if len(val_list) >= 2:
                p_name = f"Recurring Evidence: {ev}"
                p_id, _ = compute_pattern_id(p_name, [ev], PatternCategory.RECURRING_EVIDENCE.value)

                payload = {
                    "category": PatternCategory.RECURRING_EVIDENCE.value,
                    "evidence": [ev],
                    "pattern_id": p_id,
                    "pattern_name": p_name,
                }
                canonical_hash = compute_canonical_sha256(payload).upper()

                patterns.append(
                    ResearchPattern(
                        pattern_id=p_id,
                        pattern_name=p_name,
                        description=f"Evidence artifact '{ev}' is referenced across {len(val_list)} validation runs.",
                        category=PatternCategory.RECURRING_EVIDENCE,
                        evidence=[ev],
                        frequency=len(val_list),
                        confidence=min(1.0, 0.5 + 0.1 * len(val_list)),
                        supporting_clusters=[],
                        supporting_validations=sorted(val_list),
                        metadata={"evidence_id": ev},
                        canonical_hash=canonical_hash,
                    )
                )
        return sorted(patterns, key=lambda p: p.pattern_id)

    def discover_frequently_validated(
        self, validations: list[dict[str, Any]], timestamp: str
    ) -> list[ResearchPattern]:
        """Discover hypotheses or features passing validation repeatedly."""
        hyp_counts: dict[str, list[str]] = {}
        for val in validations:
            if str(val.get("status") or val.get("decision")).upper() in ("PASSED", "VALIDATED", "SUPPORTED"):
                hyp_id = str(val.get("hypothesis_id") or val.get("hypothesis") or "HYP_UNKNOWN")
                val_id = str(val.get("validation_id") or val.get("id") or "")
                if hyp_id not in hyp_counts:
                    hyp_counts[hyp_id] = []
                hyp_counts[hyp_id].append(val_id)

        patterns: list[ResearchPattern] = []
        for hyp_id, val_list in sorted(hyp_counts.items()):
            if len(val_list) >= 1:
                p_name = f"Frequently Validated: {hyp_id}"
                p_id, _ = compute_pattern_id(p_name, val_list, PatternCategory.FREQUENTLY_VALIDATED.value)

                payload = {
                    "category": PatternCategory.FREQUENTLY_VALIDATED.value,
                    "pattern_id": p_id,
                    "pattern_name": p_name,
                }
                canonical_hash = compute_canonical_sha256(payload).upper()

                patterns.append(
                    ResearchPattern(
                        pattern_id=p_id,
                        pattern_name=p_name,
                        description=f"Hypothesis '{hyp_id}' passed validation {len(val_list)} times.",
                        category=PatternCategory.FREQUENTLY_VALIDATED,
                        evidence=sorted(val_list),
                        frequency=len(val_list),
                        confidence=min(1.0, 0.7 + 0.05 * len(val_list)),
                        supporting_clusters=[],
                        supporting_validations=sorted(val_list),
                        metadata={"hypothesis_id": hyp_id},
                        canonical_hash=canonical_hash,
                    )
                )
        return sorted(patterns, key=lambda p: p.pattern_id)

    def discover_weak_evidence_regions(
        self, clusters: list[ResearchCluster], timestamp: str
    ) -> list[ResearchPattern]:
        """Identify research clusters with low confidence (< 0.50) or sparse evidence."""
        patterns: list[ResearchPattern] = []
        for c in clusters:
            if c.confidence < 0.50 or len(c.participating_validations) <= 1:
                p_name = f"Weak Evidence Region: {c.title}"
                p_id, _ = compute_pattern_id(p_name, c.participating_validations, PatternCategory.WEAK_EVIDENCE_REGION.value)

                payload = {
                    "category": PatternCategory.WEAK_EVIDENCE_REGION.value,
                    "cluster_id": c.cluster_id,
                    "pattern_id": p_id,
                    "pattern_name": p_name,
                }
                canonical_hash = compute_canonical_sha256(payload).upper()

                patterns.append(
                    ResearchPattern(
                        pattern_id=p_id,
                        pattern_name=p_name,
                        description=f"Cluster '{c.title}' has low confidence ({c.confidence:.2f}) or sparse validations.",
                        category=PatternCategory.WEAK_EVIDENCE_REGION,
                        evidence=c.participating_validations,
                        frequency=1,
                        confidence=c.confidence,
                        supporting_clusters=[c.cluster_id],
                        supporting_validations=c.participating_validations,
                        metadata={"cluster_id": c.cluster_id},
                        canonical_hash=canonical_hash,
                    )
                )
        return sorted(patterns, key=lambda p: p.pattern_id)

    def discover_all_patterns(
        self,
        validations: list[dict[str, Any]],
        clusters: list[ResearchCluster],
        timestamp: str,
    ) -> list[ResearchPattern]:
        """Discover complete set of deterministic research patterns."""
        patterns: list[ResearchPattern] = []
        patterns.extend(self.discover_recurring_evidence(validations, timestamp))
        patterns.extend(self.discover_frequently_validated(validations, timestamp))
        patterns.extend(self.discover_weak_evidence_regions(clusters, timestamp))
        return sorted(patterns, key=lambda p: p.pattern_id)
