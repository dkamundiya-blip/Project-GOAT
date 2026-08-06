"""
Project GOAT v0.7 — Deterministic Research Intelligence Engine

Calculates deterministic research intelligence metrics:
- Knowledge Density
- Evidence Density
- Validation Stability
- Consensus Stability
- Research Breadth
- Research Depth
- Knowledge Maturity
- Scientific Confidence
"""

from __future__ import annotations

from typing import Any

from goat.integration.core.models import IntegratedKnowledge
from goat.integration.graph.engine import ScientificKnowledgeGraph
from goat.meta_analysis.core.canonical import compute_canonical_sha256, compute_metrics_id
from goat.meta_analysis.core.models import ResearchIntelligenceMetrics


class ResearchIntelligenceEngine:
    """Engine for computing deterministic research intelligence metrics."""

    def compute_metrics(
        self,
        graph: ScientificKnowledgeGraph | None,
        integrated_knowledge_list: list[IntegratedKnowledge],
        validations: list[dict[str, Any]],
        conflicts: list[dict[str, Any]],
        timestamp: str,
    ) -> ResearchIntelligenceMetrics:
        """Compute complete ResearchIntelligenceMetrics model deterministically.

        Args:
            graph: Optional ScientificKnowledgeGraph object.
            integrated_knowledge_list: List of IntegratedKnowledge models.
            validations: List of validation run summaries.
            conflicts: List of conflict records.
            timestamp: ISO 8601 UTC timestamp.

        Returns:
            ResearchIntelligenceMetrics model.
        """
        nodes = graph.get_nodes() if graph else []
        edges = graph.get_edges() if graph else []

        total_nodes = len(nodes)
        validated_nodes = sum(
            1 for n in nodes if hasattr(n.node_type, "value") and n.node_type.value == "VALIDATION" or n.node_type == "VALIDATION"
        )
        knowledge_density = round(float(validated_nodes) / float(total_nodes), 4) if total_nodes > 0 else 0.0

        total_evidence = sum(len(n.metadata.get("evidence_ids", [])) + 1 for n in nodes)
        evidence_density = round(min(1.0, float(total_evidence) / float(max(1, total_nodes + len(edges)))), 4)

        total_vals = len(validations)
        passed_vals = sum(
            1 for v in validations if str(v.get("status") or v.get("decision")).upper() in ("PASSED", "VALIDATED", "SUPPORTED")
        )
        validation_stability = round(float(passed_vals) / float(total_vals), 4) if total_vals > 0 else 0.0

        consensus_scores = [ik.consensus_strength for ik in integrated_knowledge_list]
        consensus_stability = round(sum(consensus_scores) / len(consensus_scores), 4) if consensus_scores else 0.0

        unique_topics = set()
        for v in validations:
            top = v.get("hypothesis_id") or v.get("feature_id") or v.get("title")
            if top:
                unique_topics.add(str(top))
        research_breadth = float(len(unique_topics))

        # Research depth: max path length in graph traversal
        depth_val = 1.0
        if graph and nodes:
            max_trav = max([len(graph.traversal(n.node_id, max_depth=5)) for n in nodes[:5]] + [1])
            depth_val = float(max_trav)
        research_depth = round(depth_val, 4)

        knowledge_maturity = round(
            max(0.0, min(1.0, 0.4 * validation_stability + 0.3 * consensus_stability + 0.3 * knowledge_density)), 4
        )
        scientific_confidence = round(
            max(0.0, min(1.0, 0.5 * validation_stability + 0.5 * evidence_density)), 4
        )

        metrics_id, _ = compute_metrics_id(knowledge_density, evidence_density, timestamp)

        payload = {
            "evidence_density": evidence_density,
            "knowledge_density": knowledge_density,
            "metrics_id": metrics_id,
            "timestamp": timestamp,
        }
        canonical_hash = compute_canonical_sha256(payload).upper()

        return ResearchIntelligenceMetrics(
            metrics_id=metrics_id,
            knowledge_density=knowledge_density,
            evidence_density=evidence_density,
            validation_stability=validation_stability,
            consensus_stability=consensus_stability,
            research_breadth=research_breadth,
            research_depth=research_depth,
            knowledge_maturity=knowledge_maturity,
            scientific_confidence=scientific_confidence,
            timestamp=timestamp,
            canonical_hash=canonical_hash,
        )
