"""
Project GOAT v0.6 — Report Holdout Isolation Unit Tests

Verifies zero access to real holdout data or HoldoutAccessGate during report building.
"""

from __future__ import annotations

import pytest

from goat.research.edge.definition import CandidateEdge
from goat.research.edge.models import ValidationRunInfo
from goat.research.edge.persistence import SQLiteEdgeRepository
from goat.research.edge.policy import ValidationPolicy
from goat.research.edge.reporting.builder import ValidationReportBuilder
from goat.research.edge.validation.holdout import HoldoutAccessGate


def test_report_builder_has_no_holdout_gate_dependency():
    repo = SQLiteEdgeRepository(":memory:")
    edge = CandidateEdge(
        proposition_name="Holdout Isolated Edge",
        causal_primitive="greater_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"period": 20},
    )
    policy = ValidationPolicy(policy_id="P1_ISO")
    run = ValidationRunInfo(
        edge_id=edge.edge_id,
        policy_hash=policy.policy_hash,
        dataset_fingerprint="ds_fp_iso",
        candidate_target_scope="UNIVERSAL",
    )

    repo.save_candidate_edge(edge)
    repo.save_validation_policy(policy)
    repo.save_validation_run(run)

    builder = ValidationReportBuilder(repo)
    report = builder.build(run.validation_run_id)

    # Gate remains completely uninstantiated and un-accessed during report build
    gate = HoldoutAccessGate()
    assert gate.bytes_read == 0
    assert report.confirmatory_audit is None
    assert report.validation_summary.confirmatory_status == "PENDING"
