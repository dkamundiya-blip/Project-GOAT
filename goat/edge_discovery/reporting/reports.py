"""
Project GOAT v0.9 — Quantitative Edge Discovery Report Generator
"""

from typing import Any

from goat.edge_discovery.core.canonical import serialize_canonical_json
from goat.edge_discovery.core.models import (
    DiscoveryDecision,
    DiscoverySummary,
    EdgeCandidate,
    EdgeScore,
    NoveltyAssessment,
)


class EdgeDiscoveryReportGenerator:
    """Report Generator for Quantitative Edge Discovery Engine.

    Generates Markdown and Canonical JSON representations of candidate edges,
    novelty assessments, quality scores, validation decisions, and discovery summaries.
    """

    def generate_executive_report(self, summary: DiscoverySummary) -> str:
        """Generate Markdown Executive Research Report."""
        return (
            f"# QUANTITATIVE EDGE DISCOVERY EXECUTIVE REPORT\n"
            f"**Summary ID**: `{summary.summary_id}` | **Timestamp**: `{summary.timestamp}`\n"
            f"**Canonical Hash**: `{summary.canonical_hash}`\n\n"
            f"## Discovery Summary\n"
            f"- **Total Patterns Mined**: `{summary.total_patterns}`\n"
            f"- **Total Pattern Clusters**: `{summary.total_clusters}`\n"
            f"- **Total Edge Candidates**: `{summary.total_candidates}`\n"
            f"- **Protocol Validated Edges**: `{summary.total_validated}`\n"
            f"- **Rejected Candidates**: `{summary.total_rejected}`\n\n"
            f"## Category Breakdown\n"
            + "\n".join([f"- `{k}`: `{v}`" for k, v in summary.category_counts.items()])
            + "\n\n## Tier Breakdown\n"
            + "\n".join([f"- `{k}`: `{v}`" for k, v in summary.tier_counts.items()])
        )

    def generate_edge_discovery_report(self, candidate: EdgeCandidate) -> str:
        """Generate Markdown Edge Discovery Report."""
        return (
            f"# QUANTITATIVE EDGE CANDIDATE REPORT\n"
            f"**Name**: `{candidate.name}`\n"
            f"**Candidate ID**: `{candidate.candidate_id}` | **Symbol**: `{candidate.symbol}`\n"
            f"**Category**: `{candidate.category.value}` | **Canonical Hash**: `{candidate.canonical_hash}`\n\n"
            f"## Hypothesis Proposition\n"
            f"> {candidate.hypothesis_statement}\n\n"
            f"## Statistical Metrics\n"
            f"- **Confidence Level**: `{candidate.confidence_level * 100.0:.2f}%`\n"
            f"- **Observation Count**: `{candidate.observation_count}`\n"
            f"- **Pattern IDs**: `{', '.join(candidate.pattern_ids)}`\n"
        )

    def generate_novelty_report(self, novelty: NoveltyAssessment) -> str:
        """Generate Markdown Novelty Assessment Report."""
        return (
            f"# EDGE CANDIDATE NOVELTY REPORT\n"
            f"**Assessment ID**: `{novelty.assessment_id}` | **Candidate ID**: `{novelty.candidate_id}`\n"
            f"**Novelty Status**: `{novelty.status.value}` | **Canonical Hash**: `{novelty.canonical_hash}`\n\n"
            f"## Novelty Metrics\n"
            f"- **Max Similarity Score**: `{novelty.max_similarity_score:.4f}`\n"
            f"- **Is Novel**: `{novelty.is_novel}`\n"
            f"- **Closest Archived Edge**: `{novelty.closest_archived_edge_id or 'None'}`\n"
        )

    def generate_scoring_report(self, score: EdgeScore) -> str:
        """Generate Markdown Edge Quality Scoring Report."""
        return (
            f"# EDGE QUALITY SCORING REPORT\n"
            f"**Score ID**: `{score.score_id}` | **Candidate ID**: `{score.candidate_id}`\n"
            f"**Quality Tier**: `{score.quality_tier.value}` | **Canonical Hash**: `{score.canonical_hash}`\n\n"
            f"## Score Breakdown (0..100)\n"
            f"- **Overall Quality Score**: `{score.overall_score:.2f}`\n"
            f"- **Support Score**: `{score.support_score:.2f}`\n"
            f"- **Stability Score**: `{score.stability_score:.2f}`\n"
            f"- **Consistency Score**: `{score.consistency_score:.2f}`\n"
            f"- **Robustness Score**: `{score.robustness_score:.2f}`\n"
            f"- **Live Compatibility**: `{score.live_compatibility_score:.2f}`\n"
        )

    def generate_summary_report(self, decision: DiscoveryDecision) -> str:
        """Generate Markdown Protocol Validation Decision Report."""
        return (
            f"# DISCOVERY PROTOCOL VALIDATION REPORT\n"
            f"**Decision ID**: `{decision.decision_id}` | **Candidate ID**: `{decision.candidate_id}`\n"
            f"**Outcome Status**: `{decision.status.value}` | **Rejection Reason**: `{decision.rejection_reason.value}`\n"
            f"**Canonical Hash**: `{decision.canonical_hash}`\n"
        )

    def export_canonical_json(self, obj: Any) -> str:
        """Export model as canonical JSON string."""
        return serialize_canonical_json(obj)
