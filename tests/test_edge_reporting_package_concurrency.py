"""
Project GOAT v0.6 — Package Concurrency Unit Tests

Verifies safe concurrent package writing without partial package interleaving or file corruption.
"""

from __future__ import annotations

import concurrent.futures
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


def test_concurrent_package_writes_are_safe():
    repo = SQLiteEdgeRepository(":memory:")
    edge = CandidateEdge(
        proposition_name="Concurrent Package Edge",
        causal_primitive="greater_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"period": 20},
    )
    policy = ValidationPolicy(policy_id="P1_CONC_PKG")
    run = ValidationRunInfo(
        edge_id=edge.edge_id,
        policy_hash=policy.policy_hash,
        dataset_fingerprint="ds_fp_conc_pkg",
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

    with tempfile.TemporaryDirectory() as tmp_root:
        writer = EvidencePackageWriter(root_dir=tmp_root)

        def _concurrent_write():
            return writer.write_package(report, [ev])

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(_concurrent_write) for _ in range(4)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        assert len(results) == 4
        # All concurrent workers return identical final directory path
        assert len(set(results)) == 1

        final_pkg_dir = results[0]
        verifier = EvidencePackageVerifier()
        verification = verifier.verify_package(final_pkg_dir)
        assert verification["verification_status"] == "VERIFIED"
