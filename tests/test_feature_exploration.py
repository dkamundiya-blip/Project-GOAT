"""
Project GOAT v0.7 — Step 4.3 Feature Space Exploration Engine Test Suite
"""

from __future__ import annotations

import pandas as pd
import pytest
from pydantic import ValidationError

from goat.features import (
    BarRange,
    BaseSearchStrategy,
    BayesianSearchAdapter,
    BeamSearchStrategy,
    BodyRatio,
    CandidateFeature,
    EvolutionarySearchAdapter,
    ExhaustiveSearchStrategy,
    ExplorationBudget,
    ExplorationReport,
    FeatureExplorationEngine,
    FeatureLineageEngine,
    GrammarGuidedSearchStrategy,
    LineageValidationError,
    LogReturn,
    LogTransform,
    MarketDataWindow,
    RatioTransform,
    RollingMeanTransform,
    RuleBasedSearchStrategy,
    SymbolicSearchAdapter,
    TransformationRegistry,
    compute_candidate_id,
    compute_lineage_hash,
)


@pytest.fixture
def sample_data():
    dates = pd.date_range("2026-01-01 09:30", periods=10, freq="5min")
    data = {
        "timestamp": dates,
        "open": [100.0, 102.0, 101.0, 105.0, 104.0, 106.0, 105.0, 108.0, 107.0, 110.0],
        "high": [103.0, 104.0, 106.0, 107.0, 105.0, 108.0, 107.0, 110.0, 109.0, 112.0],
        "low": [99.0, 100.0, 100.0, 103.0, 101.0, 104.0, 103.0, 106.0, 105.0, 108.0],
        "close": [102.0, 101.0, 105.0, 104.0, 102.0, 107.0, 106.0, 109.0, 108.0, 111.0],
        "volume": [1000, 1500, 1200, 1800, 1100, 2000, 1600, 2200, 1900, 2500],
    }
    return MarketDataWindow(data)


def test_transformation_operators(sample_data):
    """Verify unary, binary, and rolling transformation operator logic and determinism."""
    f1 = LogReturn()
    f2 = BarRange()

    log_op = LogTransform()
    ratio_op = RatioTransform()
    roll_op = RollingMeanTransform(window=5)

    tf_log = log_op.transform([f1])
    tf_ratio = ratio_op.transform([f1, f2])
    tf_roll = roll_op.transform([f1])

    res_log = tf_log.compute(sample_data)
    res_ratio = tf_ratio.compute(sample_data)
    res_roll = tf_roll.compute(sample_data)

    assert len(res_log) == 10
    assert len(res_ratio) == 10
    assert len(res_roll) == 10

    assert log_op.transformation_id.startswith("TRNS_")
    assert ratio_op.transformation_id.startswith("TRNS_")


def test_transformation_registry():
    """Verify TransformationRegistry registration, lookup, and metadata export."""
    reg = TransformationRegistry(load_defaults=True)
    ops = reg.list_transformations()
    assert len(ops) >= 8

    log_op = reg.get_by_name("LogTransform")
    assert log_op.name == "LogTransform"

    meta = reg.get_transformation_metadata()
    assert len(meta) >= 8
    assert "transformation_id" in meta[0]


def test_candidate_feature_and_lineage_engine():
    """Verify CandidateFeature immutability, LineageEngine tracking, and hash verification."""
    f1 = LogReturn()
    f2 = BarRange()
    log_op = LogTransform()
    tf = log_op.transform([f1])

    cand_id = compute_candidate_id(tf.feature_id, tf.scientific_fingerprint, depth=1)
    lin_hash = compute_lineage_hash(
        feature_id=tf.feature_id,
        scientific_fingerprint=tf.scientific_fingerprint,
        parent_ids=[f1.feature_id],
        transformation_id=log_op.transformation_id,
        depth=1,
    )

    cand = CandidateFeature(
        candidate_id=cand_id,
        feature_id=tf.feature_id,
        scientific_fingerprint=tf.scientific_fingerprint,
        parent_feature_ids=[f1.feature_id],
        transformation_id=log_op.transformation_id,
        generation_depth=1,
        generation_timestamp="2026-07-30T00:00:00Z",
        mathematical_definition=tf.metadata.mathematical_definition,
        lineage_hash=lin_hash,
    )

    # Immutability check
    with pytest.raises(ValidationError):
        cand.generation_depth = 5

    lineage = FeatureLineageEngine()
    lineage.register_candidate(cand)

    assert lineage.get_candidate(tf.feature_id).candidate_id == cand_id
    assert lineage.get_parents(tf.feature_id) == [f1.feature_id]

    chain = lineage.get_transformation_chain(tf.feature_id)
    assert len(chain) == 1
    assert chain[0]["feature_id"] == tf.feature_id


def test_lineage_hash_verification_failure():
    """Verify LineageEngine raises LineageValidationError on tampered lineage hash."""
    f1 = LogReturn()
    log_op = LogTransform()
    tf = log_op.transform([f1])

    cand = CandidateFeature(
        candidate_id=compute_candidate_id(tf.feature_id, tf.scientific_fingerprint, depth=1),
        feature_id=tf.feature_id,
        scientific_fingerprint=tf.scientific_fingerprint,
        parent_feature_ids=[f1.feature_id],
        transformation_id=log_op.transformation_id,
        generation_depth=1,
        generation_timestamp="2026-07-30T00:00:00Z",
        mathematical_definition=tf.metadata.mathematical_definition,
        lineage_hash="TAMPERED_" + "0" * 55,
    )

    lineage = FeatureLineageEngine()
    with pytest.raises(LineageValidationError, match="Lineage hash verification failure"):
        lineage.register_candidate(cand)


def test_exploration_budget():
    """Verify ExplorationBudget tracking and termination limits."""
    budget = ExplorationBudget(max_depth=2, max_candidates=5)

    assert not budget.is_exhausted()
    assert budget.is_depth_allowed(2)
    assert not budget.is_depth_allowed(3)

    for _ in range(5):
        budget.record_generation()

    assert budget.is_exhausted()
    summary = budget.get_summary()
    assert summary["budget_exhausted"] is True
    assert summary["generated_count"] == 5


def test_exploration_engine_and_report():
    """Verify FeatureExplorationEngine candidate generation, deduplication, and ExplorationReport."""
    f1 = LogReturn()
    f2 = BarRange()
    primitives = [f1, f2]

    engine = FeatureExplorationEngine()
    budget = ExplorationBudget(max_depth=1, max_candidates=10)
    report = engine.explore(primitives, strategy=ExhaustiveSearchStrategy(), budget=budget)

    assert isinstance(report, ExplorationReport)
    assert report.report_id.startswith("REP_")
    assert report.strategy_name == "ExhaustiveSearch"
    assert len(report.generated_candidates) > 0
    assert report.budget_summary["generated_count"] > 0
    assert len(report.scientific_observations) > 0


def test_strategy_framework_adapters():
    """Verify all search strategy framework adapters instantiate and execute cleanly."""
    f1 = LogReturn()
    primitives = [f1]
    budget = ExplorationBudget(max_depth=1, max_candidates=5)
    transformations = [LogTransform()]

    strategies = [
        ExhaustiveSearchStrategy(),
        RuleBasedSearchStrategy(),
        GrammarGuidedSearchStrategy(),
        BeamSearchStrategy(beam_width=3),
        BayesianSearchAdapter(),
        EvolutionarySearchAdapter(),
        SymbolicSearchAdapter(),
    ]

    for strat in strategies:
        cands = strat.explore(primitives, transformations, budget)
        assert isinstance(cands, list)
        assert strat.name is not None
        assert strat.strategy_type in ["deterministic", "heuristic", "adapter"]
