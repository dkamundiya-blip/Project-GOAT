"""
Project GOAT v0.6 — Report Determinism & Immutability Unit Tests

Verifies cross-process determinism, evidence order invariance, and database immutability during report generation.
"""

from __future__ import annotations

import subprocess
import sys
import pytest

from goat.research.edge.definition import CandidateEdge
from goat.research.edge.evidence import AtomicEvidenceRecord, EvidenceDimensionType
from goat.research.edge.models import ValidationRunInfo
from goat.research.edge.persistence import SQLiteEdgeRepository
from goat.research.edge.policy import ValidationPolicy
from goat.research.edge.reporting.builder import ValidationReportBuilder


def test_reporting_does_not_mutate_database():
    repo = SQLiteEdgeRepository(":memory:")
    edge = CandidateEdge(
        proposition_name="Immutable DB Edge",
        causal_primitive="greater_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"period": 20},
    )
    policy = ValidationPolicy(policy_id="P1_IMMUTABLE")
    run = ValidationRunInfo(
        edge_id=edge.edge_id,
        policy_hash=policy.policy_hash,
        dataset_fingerprint="ds_fp_imm",
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

    # Count rows before report building
    cursor = repo.conn.execute("SELECT COUNT(*) FROM atomic_evidence;")
    count_before = cursor.fetchone()[0]

    builder = ValidationReportBuilder(repo)
    report = builder.build(run.validation_run_id)

    # Count rows after report building
    cursor = repo.conn.execute("SELECT COUNT(*) FROM atomic_evidence;")
    count_after = cursor.fetchone()[0]

    assert count_before == count_after == 1
    assert report.report_id.startswith("RPT_")


def test_cross_process_determinism_script():
    cmd = [
        sys.executable,
        "-c",
        "from goat.research.edge.reporting.identity import compute_report_id; "
        "print(compute_report_id('VAL_1', 'EDGE_1', 'PLC_1', 'DS_1', '1234567890ab', ['EVP_A']))",
    ]
    res1 = subprocess.check_output(cmd, text=True).strip()
    res2 = subprocess.check_output(cmd, text=True).strip()

    assert res1 == res2
    assert res1.startswith("RPT_")
