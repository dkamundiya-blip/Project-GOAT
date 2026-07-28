"""
Project GOAT v0.6 — Stage F Context Integrity & Denominator Unit Tests
"""

import pytest

from goat.research.edge.definition import CandidateEdge
from goat.research.edge.models import ValidationContextUniverse, ValidationRunInfo
from goat.research.edge.persistence import SQLiteEdgeRepository
from goat.research.edge.policy import ValidationPolicy
from goat.research.edge.validation.exceptions import StageValidationError
from goat.research.edge.validation.models import (
    ReasonCode,
    StageDecision,
    StageResult,
    ValidationStage,
)
from goat.research.edge.validation.stages.stage_f import StageFValidator


def test_context_universe_id_generation_and_immutability():
    universe = ValidationContextUniverse(contexts=("MSFT", "AAPL", "GOOGL"))
    assert universe.universe_id.startswith("CTX_")
    # Contexts are canonically sorted
    assert universe.contexts == ("AAPL", "GOOGL", "MSFT")

    # Order invariance check
    universe_reordered = ValidationContextUniverse(contexts=("GOOGL", "AAPL", "MSFT"))
    assert universe_reordered.universe_id == universe.universe_id


def test_context_universe_persistence_roundtrip():
    repo = SQLiteEdgeRepository(":memory:")
    universe = ValidationContextUniverse(contexts=("AAPL", "MSFT"))
    repo.save_context_universe(universe)

    fetched = repo.get_context_universe(universe.universe_id)
    assert fetched.universe_id == universe.universe_id
    assert fetched.contexts == universe.contexts


def test_stage_f_duplicate_context_keys_raise_error():
    """Identical or conflicting duplicate context keys MUST raise StageValidationError."""
    validator = StageFValidator()

    edge = CandidateEdge(
        proposition_name="Dedup Edge",
        causal_primitive="greater_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"period": 20},
    )
    policy = ValidationPolicy(policy_id="P1")
    run = ValidationRunInfo(
        edge_id=edge.edge_id,
        policy_hash=policy.policy_hash,
        dataset_fingerprint="ds_fp",
        candidate_target_scope="UNIVERSAL",
    )

    stage_e_res = StageResult(
        validation_run_id=run.validation_run_id,
        edge_id=edge.edge_id,
        stage=ValidationStage.STAGE_E_FALSIFICATION,
        decision=StageDecision.PASS,
        reason_code=ReasonCode.PASSED,
        policy_hash=policy.policy_hash,
    )

    # Identical duplicate context key AAPL
    contexts_identical = [
        ("AAPL", 0.45, 0.001, 200),
        ("AAPL", 0.45, 0.001, 200),
        ("MSFT", 0.50, 0.002, 200),
    ]

    with pytest.raises(StageValidationError) as excinfo:
        validator.evaluate(
            candidate_edge=edge,
            hypothesis_version="1234567890ab",
            policy=policy,
            validation_run=run,
            dataset_partitions={},
            stage_e_result=stage_e_res,
            baseline_effect=0.50,
            context_evaluations=contexts_identical,
        )
    assert "Duplicate context key 'AAPL'" in str(excinfo.value)


def test_stage_f_bound_context_universe_mismatch_raises_error():
    """StageFValidator enforces manifest match when ValidationContextUniverse is bound."""
    validator = StageFValidator()

    edge = CandidateEdge(
        proposition_name="Bound Universe Edge",
        causal_primitive="greater_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"period": 20},
    )
    policy = ValidationPolicy(policy_id="P1")
    run = ValidationRunInfo(
        edge_id=edge.edge_id,
        policy_hash=policy.policy_hash,
        dataset_fingerprint="ds_fp",
        candidate_target_scope="UNIVERSAL",
    )

    stage_e_res = StageResult(
        validation_run_id=run.validation_run_id,
        edge_id=edge.edge_id,
        stage=ValidationStage.STAGE_E_FALSIFICATION,
        decision=StageDecision.PASS,
        reason_code=ReasonCode.PASSED,
        policy_hash=policy.policy_hash,
    )

    universe = ValidationContextUniverse(contexts=("AAPL", "MSFT", "GOOGL"))

    # Missing GOOGL in caller evaluation set
    caller_subset = [
        ("AAPL", 0.45, 0.001, 200),
        ("MSFT", 0.50, 0.002, 200),
    ]

    with pytest.raises(StageValidationError) as excinfo:
        validator.evaluate(
            candidate_edge=edge,
            hypothesis_version="1234567890ab",
            policy=policy,
            validation_run=run,
            dataset_partitions={},
            stage_e_result=stage_e_res,
            baseline_effect=0.50,
            context_evaluations=caller_subset,
            context_universe=universe,
        )
    assert "Context universe mismatch" in str(excinfo.value)
