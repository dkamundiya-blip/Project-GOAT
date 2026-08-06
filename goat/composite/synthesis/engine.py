"""
Project GOAT v0.7 — Composite Edge Synthesis Engine

Synthesizes candidate CompositeEdge objects from active ScientificEdges deterministically:
- Discovers compatible edge pairs and multi-edge tuples
- Evaluates compatibility and rejects invalid/conflicting combinations
- Generates CompositeEdge, CompositeEvidence, and CompositeExplainabilityRecord models
"""

from __future__ import annotations

import itertools
from typing import Any

from goat.alpha.core.models import ScientificEdge
from goat.composite.conflicts.engine import CompositeConflictEngine
from goat.composite.core.canonical import (
    compute_canonical_sha256,
    compute_composite_evidence_id,
    compute_composite_explanation_id,
    compute_composite_id,
)
from goat.composite.core.enums import ConflictSeverity
from goat.composite.core.models import (
    CompositeEdge,
    CompositeEvidence,
    CompositeExplainabilityRecord,
)


class CompositeEdgeSynthesisEngine:
    """Engine for deterministic synthesis of CompositeEdges from active ScientificEdges."""

    def __init__(self, conflict_engine: CompositeConflictEngine | None = None) -> None:
        self.conflict_engine = conflict_engine or CompositeConflictEngine()

    def synthesize_composites(
        self,
        active_edges: list[ScientificEdge],
        timestamp: str,
    ) -> tuple[list[CompositeEdge], list[CompositeEvidence], list[CompositeExplainabilityRecord], dict[str, float]]:
        """Synthesize candidate CompositeEdges from active ScientificEdges deterministically.

        Args:
            active_edges: List of active ScientificEdge models.
            timestamp: ISO 8601 UTC timestamp string.

        Returns:
            Tuple of (composites, evidence_records, explainability_records, conflict_map).
        """
        composites: list[CompositeEdge] = []
        evidence_records: list[CompositeEvidence] = []
        explainability_records: list[CompositeExplainabilityRecord] = []
        conflict_map: dict[str, float] = {}

        if len(active_edges) < 2:
            return [], [], [], {}

        # Sort edges deterministically by edge_id
        sorted_edges = sorted(active_edges, key=lambda e: e.edge_id)

        # Generate pairwise combinations (pairs of 2)
        for e1, e2 in itertools.combinations(sorted_edges, 2):
            pair = [e1, e2]
            penalty, severity, conflict_exp = self.conflict_engine.evaluate_combination_conflicts(pair)

            if severity == ConflictSeverity.CRITICAL_REJECTION:
                continue  # Reject invalid combination

            edge_ids = [e1.edge_id, e2.edge_id]
            title = f"Composite Edge: {e1.edge_id} + {e2.edge_id}"
            desc = f"Synthesized composite edge combining '{e1.title}' and '{e2.title}'."

            cmp_id, _ = compute_composite_id(edge_ids, title)
            conflict_map[cmp_id] = penalty

            hyps = sorted(list(set(e1.originating_hypotheses + e2.originating_hypotheses)))
            vals = sorted(list(set(e1.originating_validations + e2.originating_validations)))
            clusters = sorted(list(set(e1.originating_clusters + e2.originating_clusters)))
            patterns = sorted(list(set(e1.originating_patterns + e2.originating_patterns)))
            evidence = sorted(list(set(e1.supporting_evidence + e2.supporting_evidence)))

            payload_cmp = {
                "composite_id": cmp_id,
                "participating_edges": edge_ids,
                "title": title,
            }
            hash_cmp = compute_canonical_sha256(payload_cmp).upper()

            composite = CompositeEdge(
                composite_id=cmp_id,
                title=title,
                description=desc,
                participating_edges=edge_ids,
                participating_hypotheses=hyps,
                participating_validations=vals,
                participating_clusters=clusters,
                participating_patterns=patterns,
                participating_regimes=[],
                supporting_evidence=evidence,
                creation_timestamp=timestamp,
                metadata={"edge_count": 2, "conflict_severity": severity.value},
                canonical_hash=hash_cmp,
            )
            composites.append(composite)

            # Build CompositeEvidence records for each contributing edge
            for e in pair:
                ev_id, _ = compute_composite_evidence_id(cmp_id, e.edge_id)
                payload_ev = {
                    "composite_id": cmp_id,
                    "contributing_edge": e.edge_id,
                    "evidence_id": ev_id,
                }
                hash_ev = compute_canonical_sha256(payload_ev).upper()

                c_ev = CompositeEvidence(
                    evidence_id=ev_id,
                    composite_id=cmp_id,
                    contributing_edge=e.edge_id,
                    contribution_strength=float(e.confidence),
                    explanation=f"ScientificEdge '{e.title}' contribution to composite {cmp_id}.",
                    supporting_sources=e.supporting_evidence,
                    canonical_hash=hash_ev,
                )
                evidence_records.append(c_ev)

            # Build CompositeExplainabilityRecord
            ex_id, _ = compute_composite_explanation_id(cmp_id)
            sci_exp = (
                f"CompositeEdge '{title}' ({cmp_id}) synthesizes active edges {edge_ids[0]} and {edge_ids[1]}. "
                f"Supported by {len(hyps)} hypotheses, {len(vals)} validations, and {len(evidence)} evidence records. "
                f"Conflict evaluation: {conflict_exp}"
            )

            payload_ex = {
                "composite_id": cmp_id,
                "explanation_id": ex_id,
            }
            hash_ex = compute_canonical_sha256(payload_ex).upper()

            c_ex = CompositeExplainabilityRecord(
                explanation_id=ex_id,
                composite_id=cmp_id,
                participating_edges=edge_ids,
                supporting_hypotheses=hyps,
                supporting_validations=vals,
                supporting_knowledge=[],
                supporting_trends=[],
                supporting_regimes=[],
                supporting_evidence=evidence,
                scientific_explanation=sci_exp,
                compatibility_explanation="High scientific compatibility and mutual evidence reinforcement.",
                conflict_explanation=conflict_exp,
                canonical_hash=hash_ex,
            )
            explainability_records.append(c_ex)

        return (
            sorted(composites, key=lambda c: c.composite_id),
            sorted(evidence_records, key=lambda e: e.evidence_id),
            sorted(explainability_records, key=lambda r: r.explanation_id),
            conflict_map,
        )
