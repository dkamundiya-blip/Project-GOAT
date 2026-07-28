"""
Project GOAT v0.6 — Report Integrity Unit Tests

Verifies cryptographic verification of report ID, evidence payload hashes, and chain continuity.
"""

from __future__ import annotations

import pytest

from goat.research.edge.definition import CandidateEdge
from goat.research.edge.evidence import AtomicEvidenceRecord, EvidenceDimensionType
from goat.research.edge.models import ValidationRunInfo
from goat.research.edge.persistence import SQLiteEdgeRepository
from goat.research.edge.policy import ValidationPolicy
from goat.research.edge.reporting.builder import ValidationReportBuilder
from goat.research.edge.reporting.exceptions import ReportIntegrityError
from goat.research.edge.reporting.integrity import ReportIntegrityVerifier


def test_integrity_verifier_accepts_valid_report_and_rejects_corrupted_payload():
    repo = SQLiteEdgeRepository(":memory:")
    edge = CandidateEdge(
        proposition_name="Integrity Edge",
        causal_primitive="greater_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"period": 20},
    )
    policy = ValidationPolicy(policy_id="P1_INT")
    run = ValidationRunInfo(
        edge_id=edge.edge_id,
        policy_hash=policy.policy_hash,
        dataset_fingerprint="ds_fp_int",
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

    verifier = ReportIntegrityVerifier()
    assert verifier.verify_report(report, [ev]) is True

    # Mutated evidence record with a different sample_count (valid payload hash for mutated payload)
    corrupted_ev = AtomicEvidenceRecord(
        validation_run_id=run.validation_run_id,
        edge_id=edge.edge_id,
        dimension_type=EvidenceDimensionType.DISCOVERY,
        dimension_key="disc_summary",
        partition_identity="train",
        sample_count=999,  # mutated payload produces different payload hash
        effect_size=0.35,
        effect_size_type="mean_difference",
        raw_p_value=0.001,
        statistic_value=3.5,
    )

    # Passing mutated evidence to report verifier must raise ReportIntegrityError
    with pytest.raises(ReportIntegrityError):
        verifier.verify_report(report, [corrupted_ev])
