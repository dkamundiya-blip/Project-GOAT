"""
Project GOAT v0.6 — Package Atomicity & Crash Safety Unit Tests

Verifies atomic filesystem publish using sibling .tmp_<uuid> directories and cleanup on failure.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
import pytest
from unittest.mock import patch

from goat.research.edge.definition import CandidateEdge
from goat.research.edge.evidence import AtomicEvidenceRecord, EvidenceDimensionType
from goat.research.edge.models import ValidationRunInfo
from goat.research.edge.persistence import SQLiteEdgeRepository
from goat.research.edge.policy import ValidationPolicy
from goat.research.edge.reporting import (
    EvidencePackageWriter,
    ValidationReportBuilder,
)


def test_failure_before_publish_leaves_no_partial_package():
    repo = SQLiteEdgeRepository(":memory:")
    edge = CandidateEdge(
        proposition_name="Atomic Edge",
        causal_primitive="greater_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"period": 20},
    )
    policy = ValidationPolicy(policy_id="P1_ATOMIC")
    run = ValidationRunInfo(
        edge_id=edge.edge_id,
        policy_hash=policy.policy_hash,
        dataset_fingerprint="ds_fp_atomic",
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
        final_dir = Path(tmp_root) / report.validation_run_id / report.report_id

        # Inject simulated failure right before atomic publish
        with patch("goat.research.edge.reporting.package_integrity.EvidencePackageVerifier.verify_package") as mock_verify:
            mock_verify.side_effect = RuntimeError("Simulated crash right before atomic publish")

            with pytest.raises(RuntimeError):
                writer.write_package(report, [ev])

        # Verify final package directory does not exist
        assert not final_dir.exists()

        # Verify no orphaned temporary directories remain under run folder
        run_folder = Path(tmp_root) / report.validation_run_id
        if run_folder.exists():
            assert len(list(run_folder.glob(".tmp_*"))) == 0
