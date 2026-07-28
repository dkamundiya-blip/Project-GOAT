"""
Project GOAT v0.6 — Edge Domain Models & Evidence Separation Tests

Verifies ValidationPolicy policy_hash exclusion rules, AtomicEvidenceRecord payload separation,
true nested immutability (MappingProxyType/tuple), caller input mutation isolation,
and malformed input rejection.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from goat.research.edge.definition import CandidateEdge
from goat.research.edge.enums import (
    EdgeLifecycleStatus,
    EdgeScope,
    EvidenceDimensionType,
    MultiplicityStrategy,
    ValidationStageOutcome,
)
from goat.research.edge.evidence import AtomicEvidenceRecord
from goat.research.edge.policy import ValidationPolicy


def test_validation_policy_version_and_metadata_exclusion():
    """Verify ValidationPolicy policy_hash excludes version, policy_id, and description."""
    pol1 = ValidationPolicy(
        policy_id="POLICY_A",
        version="1.0.0",
        description="Policy description A",
        stage_a_alpha=0.05,
        stage_a_effect_min=0.15,
    )

    pol2 = ValidationPolicy(
        policy_id="POLICY_B",
        version="2.5.0-diff",  # Different version text
        description="Policy description B",  # Different description
        stage_a_alpha=0.05,
        stage_a_effect_min=0.15,
    )

    assert pol1.policy_hash.startswith("PLC_")
    assert len(pol1.policy_hash) == 20
    # Version text, policy_id, description differences MUST NOT change policy_hash
    assert pol1.policy_hash == pol2.policy_hash


def test_validation_policy_all_scientific_fields_affect_hash():
    """Verify modifying any scientific threshold or strategy alters policy_hash."""
    base = ValidationPolicy(policy_id="P1")

    assert base.policy_hash != ValidationPolicy(policy_id="P1", multiplicity_strategy=MultiplicityStrategy.BONFERRONI).policy_hash
    assert base.policy_hash != ValidationPolicy(policy_id="P1", stage_a_alpha=0.01).policy_hash
    assert base.policy_hash != ValidationPolicy(policy_id="P1", stage_a_effect_min=0.20).policy_hash
    assert base.policy_hash != ValidationPolicy(policy_id="P1", stage_a_min_sample=200).policy_hash
    assert base.policy_hash != ValidationPolicy(policy_id="P1", stage_b_min_retention_ratio=0.60).policy_hash
    assert base.policy_hash != ValidationPolicy(policy_id="P1", stage_c_min_folds=10).policy_hash
    assert base.policy_hash != ValidationPolicy(policy_id="P1", stage_c_min_positive_ratio=0.80).policy_hash
    assert base.policy_hash != ValidationPolicy(policy_id="P1", stage_c_max_fold_cv=0.50).policy_hash
    assert base.policy_hash != ValidationPolicy(policy_id="P1", stage_d_perturbation_delta=0.10).policy_hash
    assert base.policy_hash != ValidationPolicy(policy_id="P1", stage_d_min_stable_ratio=0.80).policy_hash
    assert base.policy_hash != ValidationPolicy(policy_id="P1", stage_d_max_allowed_drop=0.40).policy_hash
    assert base.policy_hash != ValidationPolicy(policy_id="P1", stage_e_fail_on_contradictory_inversion=False).policy_hash
    assert base.policy_hash != ValidationPolicy(policy_id="P1", stage_f_min_replication_pct=0.75).policy_hash
    assert base.policy_hash != ValidationPolicy(policy_id="P1", stage_f_meta_alpha=0.001).policy_hash


def test_atomic_evidence_identity_and_payload_separation():
    """Verify evidence_id stays identical when result metrics change, while evidence_payload_hash changes."""
    rec_original = AtomicEvidenceRecord(
        validation_run_id="VAL_1234567890ABCDEF",
        edge_id="EDGE_1234567890ABCDEF",
        dimension_type=EvidenceDimensionType.WALK_FORWARD_FOLD,
        dimension_key="fold_3",
        partition_identity="validation",
        sample_count=250,
        effect_size=0.35,
        raw_p_value=0.002,
        statistic_value=3.10,
    )

    # Mutate RESULT metric (p-value and effect size change)
    rec_changed_results = AtomicEvidenceRecord(
        validation_run_id="VAL_1234567890ABCDEF",
        edge_id="EDGE_1234567890ABCDEF",
        dimension_type=EvidenceDimensionType.WALK_FORWARD_FOLD,
        dimension_key="fold_3",
        partition_identity="validation",
        sample_count=250,
        effect_size=0.45,
        raw_p_value=0.0001,
        statistic_value=4.20,
    )

    # Mutate OBSERVATION identity (dimension_key changes)
    rec_changed_observation = AtomicEvidenceRecord(
        validation_run_id="VAL_1234567890ABCDEF",
        edge_id="EDGE_1234567890ABCDEF",
        dimension_type=EvidenceDimensionType.WALK_FORWARD_FOLD,
        dimension_key="fold_4",
        partition_identity="validation",
        sample_count=250,
        effect_size=0.35,
        raw_p_value=0.002,
        statistic_value=3.10,
    )

    # 1. Same observation target -> SAME evidence_id
    assert rec_original.evidence_id == rec_changed_results.evidence_id
    assert rec_original.evidence_id.startswith("EVD_")

    # 2. Changed result payload -> DIFFERENT evidence_payload_hash
    assert rec_original.evidence_payload_hash != rec_changed_results.evidence_payload_hash
    assert rec_original.evidence_payload_hash.startswith("EVP_")

    # 3. Changed observation key -> DIFFERENT evidence_id
    assert rec_original.evidence_id != rec_changed_observation.evidence_id


def test_true_nested_immutability_and_caller_isolation():
    """Verify nested dicts/lists are recursively frozen and caller mutation cannot alter model state."""
    caller_dict = {"outer": {"inner": [10, 20]}, "lookback": 50}
    caller_labels = ["tag1", "tag2"]

    edge = CandidateEdge(
        proposition_name="Test Edge",
        causal_primitive="greater_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec=caller_dict,
        display_labels=caller_labels,
    )

    initial_id = edge.edge_id

    # 1. Direct mutation attempt on model attribute must fail
    with pytest.raises(TypeError):
        edge.base_condition_spec["lookback"] = 999

    with pytest.raises(TypeError):
        edge.base_condition_spec["outer"]["inner"][0] = 999

    # 2. Caller mutating their own input dictionary post-instantiation must NOT affect model
    caller_dict["lookback"] = 999
    caller_dict["outer"]["inner"].append(30)
    caller_labels.append("tag3")

    assert edge.base_condition_spec["lookback"] == 50
    assert edge.base_condition_spec["outer"]["inner"] == (10, 20)
    assert edge.display_labels == ("tag1", "tag2")
    assert edge.compute_id() == initial_id


def test_enum_consistency():
    """Verify INSUFFICIENT_EVIDENCE is consistent across lifecycle and stage outcome enums."""
    assert EdgeLifecycleStatus.INSUFFICIENT_EVIDENCE.value == "INSUFFICIENT_EVIDENCE"
    assert ValidationStageOutcome.INSUFFICIENT_EVIDENCE.value == "INSUFFICIENT_EVIDENCE"
    assert EdgeScope.UNIVERSAL.value == "UNIVERSAL"
    assert MultiplicityStrategy.BENJAMINI_HOCHBERG.value == "BENJAMINI_HOCHBERG"


def test_malformed_input_rejection():
    """Verify Pydantic validators reject malformed inputs for domain models."""
    with pytest.raises(ValueError, match="strictly between 0 and 1"):
        ValidationPolicy(policy_id="P1", stage_a_alpha=1.5)

    with pytest.raises(ValueError, match="strictly between 0 and 1"):
        ValidationPolicy(policy_id="P1", stage_a_alpha=0.0)

    with pytest.raises(ValueError, match="must be a non-empty string"):
        ValidationPolicy(policy_id="   ")

    with pytest.raises(ValueError, match="must be a non-empty string"):
        AtomicEvidenceRecord(
            validation_run_id="",
            edge_id="EDGE_123",
            dimension_type=EvidenceDimensionType.DISCOVERY,
            dimension_key="discovery",
            partition_identity="train",
            sample_count=100,
            effect_size=0.2,
            raw_p_value=0.01,
        )


def test_top_level_immutability_enforcement():
    """Verify v0.6 models are frozen and reject top-level attribute assignment."""
    pol = ValidationPolicy(policy_id="POL_IMMUTABLE")
    with pytest.raises((ValidationError, TypeError)):
        pol.stage_a_alpha = 0.01

    rec = AtomicEvidenceRecord(
        validation_run_id="VAL_123",
        edge_id="EDGE_123",
        dimension_type=EvidenceDimensionType.DISCOVERY,
        dimension_key="discovery",
        partition_identity="train",
        sample_count=100,
        effect_size=0.2,
        raw_p_value=0.01,
    )
    with pytest.raises((ValidationError, TypeError)):
        rec.sample_count = 500
