"""
Project GOAT v0.7 — Edge Evidence & Explainability Aggregator

Provides complete scientific traceability and evidence extraction for quantitative edges:
- Generates EdgeEvidence models (EEV_<HEX16>)
- Builds EdgeExplainabilityRecord models (EEX_<HEX16>)
"""

from __future__ import annotations

from typing import Any

from goat.alpha.core.canonical import (
    compute_canonical_sha256,
    compute_evidence_id,
    compute_explanation_id,
)
from goat.alpha.core.enums import EvidenceSourceType
from goat.alpha.core.models import (
    EdgeEvidence,
    EdgeExplainabilityRecord,
    ScientificEdge,
)


class EdgeEvidenceAggregator:
    """Aggregator providing deterministic evidence extraction and traceability for ScientificEdges."""

    def aggregate_evidence(
        self,
        edge: ScientificEdge,
        validations: list[dict[str, Any]],
    ) -> list[EdgeEvidence]:
        """Extract supporting EdgeEvidence records for a ScientificEdge deterministically."""
        evidence_list: list[EdgeEvidence] = []

        # 1. Validation Run evidence sources
        for val_id in sorted(edge.originating_validations):
            ev_id, _ = compute_evidence_id(edge.edge_id, val_id, EvidenceSourceType.VALIDATION.value)
            payload = {
                "edge_id": edge.edge_id,
                "evidence_id": ev_id,
                "source_reference": val_id,
            }
            canonical_hash = compute_canonical_sha256(payload).upper()

            evidence_list.append(
                EdgeEvidence(
                    evidence_id=ev_id,
                    edge_id=edge.edge_id,
                    source_type=EvidenceSourceType.VALIDATION,
                    source_reference=val_id,
                    confidence=edge.confidence,
                    reproducibility=edge.reproducibility,
                    explanation=f"Validation run '{val_id}' empirical support.",
                    canonical_hash=canonical_hash,
                )
            )

        # 2. ResearchCluster evidence sources
        for cl_id in sorted(edge.originating_clusters):
            ev_id, _ = compute_evidence_id(edge.edge_id, cl_id, EvidenceSourceType.CLUSTER.value)
            payload = {
                "edge_id": edge.edge_id,
                "evidence_id": ev_id,
                "source_reference": cl_id,
            }
            canonical_hash = compute_canonical_sha256(payload).upper()

            evidence_list.append(
                EdgeEvidence(
                    evidence_id=ev_id,
                    edge_id=edge.edge_id,
                    source_type=EvidenceSourceType.CLUSTER,
                    source_reference=cl_id,
                    confidence=edge.confidence,
                    reproducibility=edge.reproducibility,
                    explanation=f"ResearchCluster '{cl_id}' structural support.",
                    canonical_hash=canonical_hash,
                )
            )

        return sorted(evidence_list, key=lambda e: e.evidence_id)

    def build_explainability_record(
        self,
        edge: ScientificEdge,
        evidence_list: list[EdgeEvidence],
    ) -> EdgeExplainabilityRecord:
        """Construct an EdgeExplainabilityRecord establishing complete traceability for an edge."""
        origin = edge.originating_hypotheses[0] if edge.originating_hypotheses else "HYP_UNKNOWN"
        ev_ids = sorted([e.evidence_id for e in evidence_list])
        hyp_ids = sorted(edge.originating_hypotheses)
        val_ids = sorted(edge.originating_validations)
        cl_ids = sorted(edge.originating_clusters)
        tr_ids = sorted(edge.originating_trends)

        explanation = (
            f"Scientific Edge '{edge.title}' ({edge.edge_id}) is scientifically traceable to origin '{origin}'. "
            f"Supported by {len(val_ids)} validation runs, {len(cl_ids)} research clusters, and {len(ev_ids)} evidence records. "
            f"Maturity stage: {edge.maturity.value if hasattr(edge.maturity, 'value') else edge.maturity}."
        )

        exp_id, _ = compute_explanation_id(edge.edge_id, origin)

        payload = {
            "edge_id": edge.edge_id,
            "explanation_id": exp_id,
            "origin": origin,
        }
        canonical_hash = compute_canonical_sha256(payload).upper()

        return EdgeExplainabilityRecord(
            explanation_id=exp_id,
            edge_id=edge.edge_id,
            origin=origin,
            supporting_evidence=ev_ids,
            supporting_hypotheses=hyp_ids,
            supporting_experiments=val_ids,
            supporting_studies=[],
            supporting_clusters=cl_ids,
            supporting_trends=tr_ids,
            supporting_reports=[],
            scientific_explanation=explanation,
            canonical_hash=canonical_hash,
        )
