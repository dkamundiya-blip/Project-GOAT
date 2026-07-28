"""
Project GOAT v0.6 — Package Determinism Unit Tests

Verifies deterministic file checksums and scientific content hash representation.
"""

from __future__ import annotations

import tempfile
import pytest

from goat.research.edge.definition import CandidateEdge
from goat.research.edge.evidence import AtomicEvidenceRecord, EvidenceDimensionType
from goat.research.edge.models import ValidationRunInfo
from goat.research.edge.persistence import SQLiteEdgeRepository
from goat.research.edge.policy import ValidationPolicy
from goat.research.edge.reporting import (
    EvidencePackageVerifier,
    EvidencePackageWriter,
    ValidationReportBuilder,
)


def test_identical_scientific_state_produces_identical_package_structure():
    repo = SQLiteEdgeRepository(":memory:")
    edge = CandidateEdge(
        proposition_name="Determinism Package Edge",
        causal_primitive="greater_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"period": 20},
    )
    policy = ValidationPolicy(policy_id="P1_DET_PKG")
    run = ValidationRunInfo(
        edge_id=edge.edge_id,
        policy_hash=policy.policy_hash,
        dataset_fingerprint="ds_fp_det_pkg",
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

    with tempfile.TemporaryDirectory() as tmp_root1, tempfile.TemporaryDirectory() as tmp_root2:
        writer1 = EvidencePackageWriter(root_dir=tmp_root1)
        writer2 = EvidencePackageWriter(root_dir=tmp_root2)

        pkg_dir1 = writer1.write_package(report, [ev])
        pkg_dir2 = writer2.write_package(report, [ev])

        assert pkg_dir1.name == pkg_dir2.name  # RPT_<HEX16> identity matches

        # Compare content of validation_report.json and evidence.json across both runs
        rep1_json = (pkg_dir1 / "validation_report.json").read_text(encoding="utf-8")
        rep2_json = (pkg_dir2 / "validation_report.json").read_text(encoding="utf-8")
        assert rep1_json == rep2_json

        ev1_json = (pkg_dir1 / "evidence.json").read_text(encoding="utf-8")
        ev2_json = (pkg_dir2 / "evidence.json").read_text(encoding="utf-8")
        assert ev1_json == ev2_json
