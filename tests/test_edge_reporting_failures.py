"""
Project GOAT v0.6 — Failed Edge & Insufficient Evidence Reporting Unit Tests

Verifies faithful reporting for failed or insufficient evidence candidates.
"""

from __future__ import annotations

import pytest

from goat.research.edge.definition import CandidateEdge
from goat.research.edge.evidence import AtomicEvidenceRecord, EvidenceDimensionType
from goat.research.edge.models import ValidationRunInfo
from goat.research.edge.persistence import SQLiteEdgeRepository
from goat.research.edge.policy import ValidationPolicy
from goat.research.edge.reporting.builder import ValidationReportBuilder


def test_builder_reports_failed_candidate():
    repo = SQLiteEdgeRepository(":memory:")
    edge = CandidateEdge(
        proposition_name="Failed Edge",
        causal_primitive="greater_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"period": 20},
    )
    policy = ValidationPolicy(policy_id="P1_FAIL")
    run = ValidationRunInfo(
        edge_id=edge.edge_id,
        policy_hash=policy.policy_hash,
        dataset_fingerprint="ds_fp_fail",
        candidate_target_scope="UNIVERSAL",
    )

    repo.save_candidate_edge(edge)
    repo.save_validation_policy(policy)
    repo.save_validation_run(run)

    # Failed evidence (raw_p_value = 0.50 > alpha 0.05) using EvidenceDimensionType.OOS
    ev_fail = AtomicEvidenceRecord(
        validation_run_id=run.validation_run_id,
        edge_id=edge.edge_id,
        dimension_type=EvidenceDimensionType.OOS,
        dimension_key="retention_summary",
        partition_identity="validation",
        sample_count=150,
        effect_size=0.01,
        effect_size_type="mean_difference",
        raw_p_value=0.50,
        statistic_value=0.5,
    )
    repo.save_evidence_record(ev_fail)

    builder = ValidationReportBuilder(repo)
    report = builder.build(run.validation_run_id)

    assert report.validation_summary.overall_decision == "REJECTED"
    assert report.validation_summary.lifecycle_state == "REJECTED"
    assert report.stage_results[0].decision == "FAIL"
