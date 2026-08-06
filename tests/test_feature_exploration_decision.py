"""
Project GOAT v0.7 — Step 4.3-R1 Exploration Decision Test Suite
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from goat.features import (
    BarRange,
    CandidateFeature,
    DecisionValidationError,
    ExhaustiveSearchStrategy,
    ExplorationBudget,
    ExplorationDecision,
    ExplorationReport,
    FeatureExplorationEngine,
    LogReturn,
    LogTransform,
    compute_candidate_id,
    compute_decision_id,
    compute_lineage_hash,
)


def test_decision_identity_and_determinism():
    """Verify DEC_<HEX16> and decision_hash deterministic calculation."""
    dec_id1, hash1 = compute_decision_id(
        search_strategy_id="ExhaustiveSearch",
        generation_rule_id="unary_expansion",
        parent_candidate_ids=["FEAT_1111"],
        transformation_ids=["TRNS_AAAA"],
        depth=1,
    )
    dec_id2, hash2 = compute_decision_id(
        search_strategy_id="ExhaustiveSearch",
        generation_rule_id="unary_expansion",
        parent_candidate_ids=["FEAT_1111"],
        transformation_ids=["TRNS_AAAA"],
        depth=1,
    )

    assert dec_id1 == dec_id2
    assert hash1 == hash2
    assert dec_id1.startswith("DEC_")
    assert len(dec_id1) == 20
    assert len(hash1) == 64


def test_decision_model_immutability():
    """Verify ExplorationDecision model is frozen and immutable."""
    dec_id, dec_hash = compute_decision_id("StrategyA", "RuleA", ["FEAT_1"], ["TRNS_1"], 1)
    dec = ExplorationDecision(
        decision_id=dec_id,
        search_strategy_id="StrategyA",
        parent_candidate_ids=["FEAT_1"],
        transformation_ids=["TRNS_1"],
        decision_timestamp="2026-07-30T00:00:00Z",
        decision_depth=1,
        decision_hash=dec_hash,
    )

    with pytest.raises(ValidationError):
        dec.decision_depth = 5  # Frozen check


def test_candidate_decision_linkage_and_engine_validation():
    """Verify CandidateFeature linkage to ExplorationDecision and engine validation."""
    engine = FeatureExplorationEngine()

    f1 = LogReturn()
    f2 = BarRange()
    budget = ExplorationBudget(max_depth=1, max_candidates=5)

    report = engine.explore([f1, f2], strategy=ExhaustiveSearchStrategy(), budget=budget)

    assert isinstance(report, ExplorationReport)
    assert report.decision_count > 0
    assert len(report.decisions) == report.decision_count
    assert "accepted_decisions" in report.decision_statistics

    # Every candidate must carry a decision_id matching an accepted decision
    dec_ids = {d.decision_id for d in report.decisions}
    for cand in report.generated_candidates:
        assert cand.decision_id in dec_ids


def test_orphan_candidate_rejection():
    """Verify FeatureExplorationEngine rejects orphan candidates referencing missing decisions."""
    engine = FeatureExplorationEngine()

    f1 = LogReturn()
    log_op = LogTransform()
    tf = log_op.transform([f1])

    cand = CandidateFeature(
        candidate_id=compute_candidate_id(tf.feature_id, tf.scientific_fingerprint, depth=1),
        feature_id=tf.feature_id,
        scientific_fingerprint=tf.scientific_fingerprint,
        parent_feature_ids=[f1.feature_id],
        transformation_id=log_op.transformation_id,
        decision_id="DEC_MISSING_1234567",
        generation_depth=1,
        generation_timestamp="2026-07-30T00:00:00Z",
        mathematical_definition=tf.metadata.mathematical_definition,
        lineage_hash=compute_lineage_hash(tf.feature_id, tf.scientific_fingerprint, [f1.feature_id], log_op.transformation_id, 1),
    )

    # Strategy returning orphan candidate
    class OrphanStrategy:
        name = "OrphanStrategy"
        def explore(self, primitives, transformations, budget):
            return [cand]

    with pytest.raises(DecisionValidationError, match="Orphan candidate detected"):
        engine.explore([f1], strategy=OrphanStrategy())
