"""
Project GOAT v0.6 — Report Builder Unit Tests

Verifies constructing ValidationReport from persisted SQLiteEdgeRepository state.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from goat.research.edge.definition import CandidateEdge
from goat.research.edge.evidence import AtomicEvidenceRecord, EvidenceDimensionType
from goat.research.edge.models import ValidationRunInfo
from goat.research.edge.persistence import SQLiteEdgeRepository
from goat.research.edge.policy import ValidationPolicy
from goat.research.edge.reporting.builder import ValidationReportBuilder
from goat.research.edge.reporting.serializer import render_report_markdown, serialize_report_to_json


def test_builder_constructs_valid_report_from_persisted_state():
    repo = SQLiteEdgeRepository(":memory:")
    edge = CandidateEdge(
        proposition_name="Reported Edge",
        causal_primitive="greater_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"period": 20},
    )
    policy = ValidationPolicy(policy_id="P1_REP")
    run = ValidationRunInfo(
        edge_id=edge.edge_id,
        policy_hash=policy.policy_hash,
        dataset_fingerprint="ds_fp_rep",
        candidate_target_scope="UNIVERSAL",
    )

    repo.save_candidate_edge(edge)
    repo.save_validation_policy(policy)
    repo.save_validation_run(run)

    ev = AtomicEvidenceRecord(
        validation_run_id=run.validation_run_id,
        edge_id=edge.edge_id,
        dimension_type=EvidenceDimensionType.DISCOVERY,
        dimension_key="disc_summary",
        partition_identity="train",
        sample_count=150,
        effect_size=0.35,
        effect_size_type="mean_difference",
        raw_p_value=0.001,
        statistic_value=3.5,
    )
    repo.save_evidence_record(ev)

    builder = ValidationReportBuilder(repo)
    report = builder.build(run.validation_run_id)

    assert report.validation_run_id == run.validation_run_id
    assert report.edge_identity.edge_id == edge.edge_id
    assert report.policy_specification.policy_hash == policy.policy_hash
    assert report.integrity.evidence_count == 1

    json_str = serialize_report_to_json(report)
    assert run.validation_run_id in json_str

    md_str = render_report_markdown(report)
    assert "# Project GOAT v0.6 — Scientific Edge Validation Report" in md_str
