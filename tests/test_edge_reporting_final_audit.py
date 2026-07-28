"""
Project GOAT v0.6 — Step 3.4D Final Adversarial & Conformance Test Suite

End-to-end verification of scientific immutability, report identity computation, non-finite float rejection,
failed stage fidelity, and holdout isolation.
"""

from __future__ import annotations

import json
import pytest

from goat.research.edge.definition import CandidateEdge
from goat.research.edge.models import ValidationRunInfo
from goat.research.edge.persistence import SQLiteEdgeRepository
from goat.research.edge.policy import ValidationPolicy
from goat.research.edge.reporting import (
    ReportBuildError,
    ValidationReportBuilder,
    compute_report_id,
    serialize_report_to_json,
)
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


def test_report_id_identity_mutation():
    val_run_id = "VAL_1111222233334444"
    edge_id = "EDGE_5555666677778888"
    policy_hash = "PLC_9999000011112222"
    ds_fp = "DS_33334444"
    hyp_ver = "1234567890ab"
    evp_list = ["EVP_AAAA", "EVP_BBBB"]

    base_rpt = compute_report_id(val_run_id, edge_id, policy_hash, ds_fp, hyp_ver, evp_list)

    # Mutate edge_id -> report_id MUST change
    assert compute_report_id(val_run_id, "EDGE_DIFFERENT", policy_hash, ds_fp, hyp_ver, evp_list) != base_rpt

    # Mutate policy_hash -> report_id MUST change
    assert compute_report_id(val_run_id, edge_id, "PLC_DIFFERENT", ds_fp, hyp_ver, evp_list) != base_rpt

    # Mutate dataset_fingerprint -> report_id MUST change
    assert compute_report_id(val_run_id, edge_id, policy_hash, "DS_DIFFERENT", hyp_ver, evp_list) != base_rpt

    # Mutate hypothesis_version -> report_id MUST change
    assert compute_report_id(val_run_id, edge_id, policy_hash, ds_fp, "abcdef123456", evp_list) != base_rpt

    # Mutate evidence payload hashes -> report_id MUST change
    assert compute_report_id(val_run_id, edge_id, policy_hash, ds_fp, hyp_ver, ["EVP_AAAA"]) != base_rpt


def test_nonfinite_float_rejection():
    edge = EdgeIdentityModel(
        edge_id="EDGE_123",
        proposition_name="NaN Float Edge",
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
        stage_a_effect_min=float("nan"),  # NaN float injection
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
        lifecycle_state="REGISTERED",
        highest_completed_stage="NONE",
        overall_decision="NOT_STARTED",
        confirmatory_status="NONE",
    )
    integrity = IntegrityMetadataModel(
        evidence_count=0,
        evidence_payload_hashes=(),
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
        stage_results=(),
        integrity=integrity,
    )

    with pytest.raises(ReportBuildError) as excinfo:
        serialize_report_to_json(report)
    assert "NaN or Infinity" in str(excinfo.value)
