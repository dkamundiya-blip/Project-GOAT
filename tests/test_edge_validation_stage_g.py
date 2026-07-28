"""
Project GOAT v0.6 — Stage G Confirmatory Holdout Validation Adversarial Unit Test Suite

Verifies strict pre-access authorization, single-shot holdout access, crash safety,
AUD_ identity binding, state machine transitions, durable restart isolation, and schema v1->v2 upgrade using SYNTHETIC fixtures only.
"""

from __future__ import annotations

import sqlite3
import numpy as np
import pandas as pd
import pytest

from goat.research.edge.definition import CandidateEdge
from goat.research.edge.enums import EdgeLifecycleStatus, EvidenceDimensionType
from goat.research.edge.models import (
    ValidationContextUniverse,
    ValidationRunInfo,
    compute_confirmatory_audit_id,
)
from goat.research.edge.persistence import SQLiteEdgeRepository
from goat.research.edge.persistence.schema import initialize_database
from goat.research.edge.policy import ValidationPolicy
from goat.research.edge.validation.exceptions import HoldoutAccessError, StageValidationError
from goat.research.edge.validation.holdout import HoldoutAccessGate
from goat.research.edge.validation.models import (
    HoldoutState,
    ReasonCode,
    StageDecision,
    StageResult,
    ValidationStage,
)
from goat.research.edge.validation.stages.stage_g import StageGValidator


@pytest.fixture
def sample_edge():
    return CandidateEdge(
        proposition_name="Holdout Test Edge",
        causal_primitive="greater_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"period": 20},
    )


@pytest.fixture
def sample_policy():
    return ValidationPolicy(policy_id="P1_HOLDOUT", stage_a_alpha=0.05, stage_a_effect_min=0.15)


@pytest.fixture
def sample_run(sample_edge, sample_policy):
    return ValidationRunInfo(
        edge_id=sample_edge.edge_id,
        policy_hash=sample_policy.policy_hash,
        dataset_fingerprint="ds_fingerprint_synthetic_123",
        candidate_target_scope="UNIVERSAL",
    )


@pytest.fixture
def sample_stage_f_pass(sample_run, sample_policy):
    return StageResult(
        validation_run_id=sample_run.validation_run_id,
        edge_id=sample_run.edge_id,
        stage=ValidationStage.STAGE_F_REPLICATION,
        decision=StageDecision.PASS,
        reason_code=ReasonCode.PASSED,
        policy_hash=sample_policy.policy_hash,
    )


@pytest.fixture
def synthetic_holdout_partitions():
    np.random.seed(42)
    # Generate 150 samples with mean effect = 0.35 (> 0.15) and significant p-value
    effects = np.random.normal(loc=0.35, scale=0.5, size=150)
    df_holdout = pd.DataFrame({"effect": effects})
    return {"holdout": df_holdout}


# =============================================================================
# 1. AUTHORIZATION TESTS (1-10)
# =============================================================================

def test_stage_g_blocked_when_stage_f_fails(sample_edge, sample_policy, sample_run, synthetic_holdout_partitions):
    validator = StageGValidator()
    gate = HoldoutAccessGate()

    stage_f_fail = StageResult(
        validation_run_id=sample_run.validation_run_id,
        edge_id=sample_run.edge_id,
        stage=ValidationStage.STAGE_F_REPLICATION,
        decision=StageDecision.FAIL,
        reason_code=ReasonCode.REPLICATION_FAILED,
        policy_hash=sample_policy.policy_hash,
    )

    res = validator.evaluate(
        candidate_edge=sample_edge,
        hypothesis_version="1234567890ab",
        policy=sample_policy,
        validation_run=sample_run,
        dataset_partitions=synthetic_holdout_partitions,
        stage_f_result=stage_f_fail,
        baseline_effect=0.35,
        holdout_gate=gate,
    )

    assert res.decision == StageDecision.FAIL
    assert res.reason_code == ReasonCode.PREREQUISITE_FAILED
    assert gate.current_state == HoldoutState.SEALED
    assert gate.bytes_read == 0


def test_stage_g_blocked_when_stage_f_insufficient(sample_edge, sample_policy, sample_run, synthetic_holdout_partitions):
    validator = StageGValidator()
    gate = HoldoutAccessGate()

    stage_f_insufficient = StageResult(
        validation_run_id=sample_run.validation_run_id,
        edge_id=sample_run.edge_id,
        stage=ValidationStage.STAGE_F_REPLICATION,
        decision=StageDecision.INSUFFICIENT_EVIDENCE,
        reason_code=ReasonCode.INSUFFICIENT_CONTEXTS,
        policy_hash=sample_policy.policy_hash,
    )

    res = validator.evaluate(
        candidate_edge=sample_edge,
        hypothesis_version="1234567890ab",
        policy=sample_policy,
        validation_run=sample_run,
        dataset_partitions=synthetic_holdout_partitions,
        stage_f_result=stage_f_insufficient,
        baseline_effect=0.35,
        holdout_gate=gate,
    )

    assert res.decision == StageDecision.FAIL
    assert gate.bytes_read == 0


def test_stage_g_blocked_on_edge_id_mismatch(sample_edge, sample_policy, sample_run, sample_stage_f_pass, synthetic_holdout_partitions):
    validator = StageGValidator()
    gate = HoldoutAccessGate()

    wrong_edge = CandidateEdge(
        proposition_name="Wrong Edge",
        causal_primitive="less_than",
        target_feature="open",
        economic_rationale_category="value",
        base_condition_spec={"period": 10},
    )

    with pytest.raises(StageValidationError) as excinfo:
        validator.evaluate(
            candidate_edge=wrong_edge,
            hypothesis_version="1234567890ab",
            policy=sample_policy,
            validation_run=sample_run,
            dataset_partitions=synthetic_holdout_partitions,
            stage_f_result=sample_stage_f_pass,
            baseline_effect=0.35,
            holdout_gate=gate,
        )
    assert "edge_id mismatch" in str(excinfo.value)
    assert gate.bytes_read == 0


def test_stage_g_blocked_on_policy_hash_mismatch(sample_edge, sample_policy, sample_run, sample_stage_f_pass, synthetic_holdout_partitions):
    validator = StageGValidator()
    gate = HoldoutAccessGate()

    wrong_policy = ValidationPolicy(policy_id="P2_DIFFERENT", stage_a_alpha=0.01)

    with pytest.raises(StageValidationError) as excinfo:
        validator.evaluate(
            candidate_edge=sample_edge,
            hypothesis_version="1234567890ab",
            policy=wrong_policy,
            validation_run=sample_run,
            dataset_partitions=synthetic_holdout_partitions,
            stage_f_result=sample_stage_f_pass,
            baseline_effect=0.35,
            holdout_gate=gate,
        )
    assert "policy_hash mismatch" in str(excinfo.value)
    assert gate.bytes_read == 0


def test_stage_g_blocked_on_expected_audit_id_mismatch(sample_edge, sample_policy, sample_run, sample_stage_f_pass, synthetic_holdout_partitions):
    validator = StageGValidator()
    gate = HoldoutAccessGate()

    with pytest.raises(HoldoutAccessError) as excinfo:
        validator.evaluate(
            candidate_edge=sample_edge,
            hypothesis_version="1234567890ab",
            policy=sample_policy,
            validation_run=sample_run,
            dataset_partitions=synthetic_holdout_partitions,
            stage_f_result=sample_stage_f_pass,
            baseline_effect=0.35,
            holdout_gate=gate,
            expected_audit_id="AUD_WRONGAUDITID12",
        )
    assert "Confirmatory audit ID mismatch" in str(excinfo.value)
    assert gate.bytes_read == 0


# =============================================================================
# 2. STATE MACHINE TESTS (11-16)
# =============================================================================

def test_holdout_access_gate_legal_transitions():
    gate = HoldoutAccessGate()
    assert gate.current_state == HoldoutState.SEALED

    audit_id = gate.authorize_access(
        edge_id="EDGE_123",
        hypothesis_version="1234567890ab",
        policy_hash="PLC_123",
        dataset_fingerprint="DS_123",
        holdout_partition_identity="holdout_sealed_v1",
        validation_run_id="VAL_123",
    )
    assert gate.current_state == HoldoutState.AUTHORIZED
    assert audit_id.startswith("AUD_")

    data = gate.access_holdout(lambda: b"synthetic_data_bytes")
    assert data == b"synthetic_data_bytes"
    assert gate.current_state == HoldoutState.CONSUMED


def test_holdout_access_gate_illegal_transitions_rejected():
    gate = HoldoutAccessGate()

    # Access without authorization -> Rejected
    with pytest.raises(HoldoutAccessError) as excinfo:
        gate.access_holdout(lambda: b"data")
    assert "Gate is SEALED" in str(excinfo.value)

    # Double authorization -> Rejected
    gate.authorize_access("E", "H", "P", "D", "HP", "V")
    with pytest.raises(HoldoutAccessError) as excinfo:
        gate.authorize_access("E", "H", "P", "D", "HP", "V")
    assert "gate must be SEALED" in str(excinfo.value)

    # Access after consumed -> Rejected
    gate.access_holdout(lambda: b"data")
    assert gate.current_state == HoldoutState.CONSUMED

    with pytest.raises(HoldoutAccessError) as excinfo:
        gate.access_holdout(lambda: b"data2")
    assert "Gate is CONSUMED" in str(excinfo.value)


# =============================================================================
# 3. ONE-SHOT SCIENCE & ANTI-OPTIMIZATION TESTS (17-24)
# =============================================================================

def test_stage_g_single_shot_success_and_second_execution_blocked(sample_edge, sample_policy, sample_run, sample_stage_f_pass, synthetic_holdout_partitions):
    validator = StageGValidator()
    gate = HoldoutAccessGate()

    res = validator.evaluate(
        candidate_edge=sample_edge,
        hypothesis_version="1234567890ab",
        policy=sample_policy,
        validation_run=sample_run,
        dataset_partitions=synthetic_holdout_partitions,
        stage_f_result=sample_stage_f_pass,
        baseline_effect=0.35,
        holdout_gate=gate,
    )

    assert res.decision == StageDecision.PASS
    assert gate.current_state == HoldoutState.CONSUMED
    assert gate.bytes_read > 0

    # Attempting second execution on consumed gate must raise HoldoutAccessError
    with pytest.raises(HoldoutAccessError):
        validator.evaluate(
            candidate_edge=sample_edge,
            hypothesis_version="1234567890ab",
            policy=sample_policy,
            validation_run=sample_run,
            dataset_partitions=synthetic_holdout_partitions,
            stage_f_result=sample_stage_f_pass,
            baseline_effect=0.35,
            holdout_gate=gate,
        )


# =============================================================================
# 4. AUDIT & PERSISTENCE TESTS (25-33)
# =============================================================================

def test_confirmatory_audit_and_evidence_persistence_roundtrip(sample_edge, sample_policy, sample_run, sample_stage_f_pass, synthetic_holdout_partitions):
    repo = SQLiteEdgeRepository(":memory:")
    repo.save_candidate_edge(sample_edge)
    repo.save_validation_policy(sample_policy)
    repo.save_validation_run(sample_run)

    validator = StageGValidator()
    gate = HoldoutAccessGate()

    res = validator.evaluate(
        candidate_edge=sample_edge,
        hypothesis_version="1234567890ab",
        policy=sample_policy,
        validation_run=sample_run,
        dataset_partitions=synthetic_holdout_partitions,
        stage_f_result=sample_stage_f_pass,
        baseline_effect=0.35,
        holdout_gate=gate,
        audit_repo=repo,
    )

    assert res.decision == StageDecision.PASS
    audit_id = gate.audit_id

    # Retrieve audit metadata from repository
    fetched_audit = repo.get_confirmatory_audit(audit_id)
    assert fetched_audit["audit_id"] == audit_id
    assert fetched_audit["validation_run_id"] == sample_run.validation_run_id
    assert fetched_audit["policy_hash"] == sample_policy.policy_hash

    # Retrieve evidence from repository
    ev_id = res.evidence_ids[0]
    fetched_ev = repo.get_evidence_record(ev_id)
    assert fetched_ev.dimension_type == EvidenceDimensionType.CONFIRMATORY


def test_durable_process_restart_prevents_reexecution(sample_edge, sample_policy, sample_run, sample_stage_f_pass, synthetic_holdout_partitions):
    repo = SQLiteEdgeRepository(":memory:")
    repo.save_candidate_edge(sample_edge)
    repo.save_validation_policy(sample_policy)
    repo.save_validation_run(sample_run)

    validator = StageGValidator()
    gate1 = HoldoutAccessGate()

    # Process 1 executes Stage G and persists audit
    res1 = validator.evaluate(
        candidate_edge=sample_edge,
        hypothesis_version="1234567890ab",
        policy=sample_policy,
        validation_run=sample_run,
        dataset_partitions=synthetic_holdout_partitions,
        stage_f_result=sample_stage_f_pass,
        baseline_effect=0.35,
        holdout_gate=gate1,
        audit_repo=repo,
    )
    assert res1.decision == StageDecision.PASS

    # Process 2 starts fresh with a new SEALED HoldoutAccessGate instance
    gate2 = HoldoutAccessGate()
    assert gate2.current_state == HoldoutState.SEALED

    # Stage G must fail closed because repo already contains the audit record for this run
    with pytest.raises(HoldoutAccessError) as excinfo:
        validator.evaluate(
            candidate_edge=sample_edge,
            hypothesis_version="1234567890ab",
            policy=sample_policy,
            validation_run=sample_run,
            dataset_partitions=synthetic_holdout_partitions,
            stage_f_result=sample_stage_f_pass,
            baseline_effect=0.35,
            holdout_gate=gate2,
            audit_repo=repo,
        )
    assert "already exists in persistence store" in str(excinfo.value)
    assert gate2.current_state == HoldoutState.SEALED
    assert gate2.bytes_read == 0


def test_schema_v1_to_v2_transactional_migration():
    conn = sqlite3.connect(":memory:")
    # Initialize schema migrations table with version 1
    conn.execute("CREATE TABLE schema_migrations (version INTEGER PRIMARY KEY, applied_at_utc TEXT NOT NULL);")
    conn.execute("INSERT INTO schema_migrations (version, applied_at_utc) VALUES (1, '2026-07-28T00:00:00Z');")
    conn.execute(
        """
        CREATE TABLE validation_policies (
            policy_hash TEXT PRIMARY KEY, policy_id TEXT NOT NULL, version TEXT NOT NULL,
            description TEXT NOT NULL, multiplicity_strategy TEXT NOT NULL,
            stage_a_alpha REAL NOT NULL, stage_a_effect_min REAL NOT NULL, stage_a_min_sample INTEGER NOT NULL,
            stage_b_min_retention_ratio REAL NOT NULL, stage_c_min_folds INTEGER NOT NULL,
            stage_c_min_positive_ratio REAL NOT NULL, stage_c_max_fold_cv REAL NOT NULL,
            stage_d_perturbation_delta REAL NOT NULL, stage_d_min_stable_ratio REAL NOT NULL,
            stage_d_max_allowed_drop REAL NOT NULL, stage_e_fail_on_contradictory_inversion INTEGER NOT NULL,
            stage_f_min_replication_pct REAL NOT NULL, stage_f_meta_alpha REAL NOT NULL, created_at_utc TEXT NOT NULL
        );
        """
    )
    conn.commit()

    # Trigger initialization/migration
    initialize_database(conn)

    cursor = conn.execute("SELECT MAX(version) FROM schema_migrations;")
    assert cursor.fetchone()[0] == 2

    # Verify column meta_analysis_method was added to validation_policies
    cursor = conn.execute("PRAGMA table_info(validation_policies);")
    cols = [c[1] for c in cursor.fetchall()]
    assert "meta_analysis_method" in cols
    conn.close()


# =============================================================================
# 5. CRASH SAFETY TESTS (34-38)
# =============================================================================

def test_crash_during_holdout_access_locks_gate_as_consumed():
    gate = HoldoutAccessGate()
    gate.authorize_access("E", "H", "P", "D", "HP", "V")
    assert gate.current_state == HoldoutState.AUTHORIZED

    def _failing_accessor():
        raise RuntimeError("Simulated synthetic disk failure during holdout read")

    with pytest.raises(HoldoutAccessError) as excinfo:
        gate.access_holdout(_failing_accessor)

    assert "Simulated synthetic disk failure" in str(excinfo.value)
    # Fail closed: Crash after ACCESSED lock must force CONSUMED state, never SEALED or AUTHORIZED!
    assert gate.current_state == HoldoutState.CONSUMED


# =============================================================================
# 6. DETERMINISM TESTS (39-41)
# =============================================================================

def test_aud_identity_determinism():
    aud1 = compute_confirmatory_audit_id(
        validation_run_id="VAL_1111222233334444",
        frozen_hypothesis_version="1234567890ab",
        dataset_fingerprint="DS_FP_9999",
        policy_hash="PLC_8888777766665555",
        holdout_partition_identity="holdout_sealed_v1",
    )

    aud2 = compute_confirmatory_audit_id(
        validation_run_id="VAL_1111222233334444",
        frozen_hypothesis_version="1234567890ab",
        dataset_fingerprint="DS_FP_9999",
        policy_hash="PLC_8888777766665555",
        holdout_partition_identity="holdout_sealed_v1",
    )

    assert aud1 == aud2
    assert aud1.startswith("AUD_")
