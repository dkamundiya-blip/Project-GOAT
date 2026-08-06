"""
Project GOAT v0.9 — Quantitative Edge Discovery Novelty Assessment Engine
"""

from typing import Any

from goat.edge_discovery.core.canonical import compute_novelty_assessment_id
from goat.edge_discovery.core.enums import NoveltyStatus
from goat.edge_discovery.core.models import EdgeCandidate, NoveltyAssessment


class NoveltyAssessmentEngine:
    """Quantitative Sub-Engine for Novelty Assessment.

    Measures whether a discovered candidate quantitative edge is genuinely different
    from previously archived candidate edges to prevent duplicate submissions.
    """

    def evaluate_novelty(
        self,
        candidate: EdgeCandidate,
        archived_candidates: list[EdgeCandidate],
        max_similarity_threshold: float = 0.85,
        metadata: dict[str, Any] | None = None,
    ) -> NoveltyAssessment:
        """Evaluate candidate edge novelty against archived edges."""
        meta = dict(metadata or {})

        if not archived_candidates:
            n_id, n_hash = compute_novelty_assessment_id(
                candidate_id=candidate.candidate_id,
                similarity_score=0.0,
                status=NoveltyStatus.GENUINELY_NOVEL.value,
            )
            return NoveltyAssessment(
                assessment_id=n_id,
                candidate_id=candidate.candidate_id,
                max_similarity_score=0.0,
                closest_archived_edge_id=None,
                status=NoveltyStatus.GENUINELY_NOVEL,
                is_novel=True,
                metadata=meta,
                canonical_hash=n_hash,
            )

        max_sim = 0.0
        closest_id = None

        for arch in archived_candidates:
            if arch.candidate_id == candidate.candidate_id:
                continue

            sim = self._compute_similarity(candidate, arch)
            if sim > max_sim:
                max_sim = sim
                closest_id = arch.candidate_id

        if max_sim >= max_similarity_threshold:
            status = NoveltyStatus.DUPLICATE_EXISTS
            is_novel = False
        elif max_sim >= 0.50:
            status = NoveltyStatus.MODERATE_NOVELTY
            is_novel = True
        else:
            status = NoveltyStatus.GENUINELY_NOVEL
            is_novel = True

        n_id, n_hash = compute_novelty_assessment_id(
            candidate_id=candidate.candidate_id,
            similarity_score=max_sim,
            status=status.value,
        )

        return NoveltyAssessment(
            assessment_id=n_id,
            candidate_id=candidate.candidate_id,
            max_similarity_score=round(max_sim, 6),
            closest_archived_edge_id=closest_id,
            status=status,
            is_novel=is_novel,
            metadata=meta,
            canonical_hash=n_hash,
        )

    def _compute_similarity(self, c1: EdgeCandidate, c2: EdgeCandidate) -> float:
        if c1.symbol.upper() != c2.symbol.upper():
            return 0.10

        if c1.category != c2.category:
            return 0.30

        # Pattern overlap
        set1 = set(c1.pattern_ids)
        set2 = set(c2.pattern_ids)
        if not set1 or not set2:
            return 0.50

        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union if union > 0 else 0.0
