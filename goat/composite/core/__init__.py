"""
Project GOAT v0.7 — Composite Core Package
"""

from goat.composite.core.canonical import (
    compute_composite_evidence_id,
    compute_composite_explanation_id,
    compute_composite_id,
    compute_composite_ranking_id,
    compute_composite_report_id,
    compute_composite_score_id,
    serialize_canonical_json,
)
from goat.composite.core.enums import (
    ConflictSeverity,
    RankingStrategy,
    SynthesisMode,
)
from goat.composite.core.models import (
    CompositeEdge,
    CompositeEvidence,
    CompositeExplainabilityRecord,
    CompositeRanking,
    CompositeScore,
)

__all__ = [
    "SynthesisMode",
    "ConflictSeverity",
    "RankingStrategy",
    "CompositeEdge",
    "CompositeEvidence",
    "CompositeScore",
    "CompositeRanking",
    "CompositeExplainabilityRecord",
    "compute_composite_id",
    "compute_composite_evidence_id",
    "compute_composite_score_id",
    "compute_composite_ranking_id",
    "compute_composite_explanation_id",
    "compute_composite_report_id",
    "serialize_canonical_json",
]
