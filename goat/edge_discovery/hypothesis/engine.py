"""
Project GOAT Phase 6 — Hypothesis Engine (`goat.edge_discovery.hypothesis`)

Constructs, parses, validates, and manages immutable ResearchHypothesis instances.
"""

from __future__ import annotations

import datetime
from typing import Sequence

from goat.edge_discovery.models.hypothesis import (
    HypothesisCondition,
    HypothesisOperator,
    HypothesisPrediction,
    HypothesisStatus,
    ResearchHypothesis,
    compute_hypothesis_id,
)
from goat.research.edge.canonical import compute_canonical_sha256


class HypothesisEngine:
    """Hypothesis Engine constructing immutable quantitative research hypotheses."""

    def __init__(self, author: str = "GOAT_QUANT_ENGINE", version: str = "6.0.0"):
        self.author = author
        self.version = version

    def create_hypothesis(
        self,
        description: str,
        conditions: Sequence[HypothesisCondition],
        prediction: HypothesisPrediction,
        metadata: dict | None = None,
    ) -> ResearchHypothesis:
        """Create a fully validated immutable ResearchHypothesis."""
        cond_list = list(conditions)
        hyp_id, canon_hash = compute_hypothesis_id(cond_list, prediction, version=self.version)
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        checksum = compute_canonical_sha256(
            {
                "author": self.author,
                "condition_count": len(cond_list),
                "description": description,
                "hypothesis_id": hyp_id,
                "target_feature": prediction.target_feature,
                "version": self.version,
            }
        )

        return ResearchHypothesis(
            hypothesis_id=hyp_id,
            version=self.version,
            description=description,
            conditions=cond_list,
            prediction=prediction,
            creation_timestamp=now_iso,
            author=self.author,
            status=HypothesisStatus.DRAFT,
            checksum=checksum,
            metadata=metadata or {},
            canonical_hash=canon_hash,
        )
