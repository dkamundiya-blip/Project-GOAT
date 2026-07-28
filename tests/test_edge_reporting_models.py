"""
Project GOAT v0.6 — Reporting Models Unit Tests
"""

from __future__ import annotations

import pytest

from goat.research.edge.reporting.models import (
    DataProvenanceModel,
    EdgeIdentityModel,
    HypothesisIdentityModel,
    IntegrityMetadataModel,
    PolicySpecificationModel,
    StageSummaryModel,
    ValidationReport,
    ValidationSummaryModel,
)


def test_validation_report_immutability():
    edge = EdgeIdentityModel(
        edge_id="EDGE_123",
        proposition_name="Test Edge",
        causal_primitive="greater_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"period": 20},
    )
    hyp = HypothesisIdentityModel(
        hypothesis_version="1234567890ab",
        condition_parameters={"period": 20},
        forward_outcome_metric="return",
        forward_horizon=5,
    )
    policy = PolicySpecificationModel(
        policy_hash="PLC_123",
        policy_id="P1",
        version="1.0.0",
        multiplicity_strategy="BENJAMINI_HOCHBERG",
        meta_analysis_method="FISHER_COMBINED_PROBABILITY",
        stage_a_alpha=0.05,
        stage_a_effect_min=0.15,
        stage_a_min_sample=100,
        stage_b_min_retention_ratio=0.50,
        stage_c_min_folds=5,
        stage_c_min_positive_ratio=0.70,
        stage_c_max_fold_cv=1.00,
        stage_d_perturbation_delta=0.20,
        stage_d_min_stable_ratio=0.65,
        stage_d_max_allowed_drop=0.60,
        stage_e_fail_on_contradictory_inversion=True,
        stage_f_min_replication_pct=0.60,
        stage_f_meta_alpha=0.01,
    )
    prov = DataProvenanceModel(dataset_fingerprint="DS_123", candidate_target_scope="UNIVERSAL")
    summary = ValidationSummaryModel(
        lifecycle_state="CONFIRMATORY_READY",
        highest_completed_stage="STAGE_F_REPLICATION",
        overall_decision="PRECONFIRMATORY_PASS",
        confirmatory_status="PENDING",
    )
    integrity = IntegrityMetadataModel(
        evidence_count=1,
        evidence_payload_hashes=("EVP_123",),
        report_content_hash="RPT_1234567890ABCDEF",
    )

    report = ValidationReport(
        report_id="RPT_1234567890ABCDEF",
        validation_run_id="VAL_123",
        generated_at_utc="2026-07-28T00:00:00Z",
        edge_identity=edge,
        hypothesis_identity=hyp,
        policy_specification=policy,
        data_provenance=prov,
        validation_summary=summary,
        stage_results=(StageSummaryModel(stage="STAGE_A_DISCOVERY", decision="PASS", reason_code="PASSED"),),
        integrity=integrity,
    )

    assert report.report_id == "RPT_1234567890ABCDEF"
    with pytest.raises(Exception):  # Catch Pydantic ValidationError / TypeError on mutation
        report.report_id = "MUTATED"
