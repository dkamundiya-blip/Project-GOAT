"""
Project GOAT v0.7 — Step 4.6 Scientific Experiment Engine Test Suite
"""

from __future__ import annotations

import os
import tempfile
import pytest
from pydantic import ValidationError

from goat.experiments import (
    ExperimentAuditEvent,
    ExperimentContext,
    ExperimentExecutor,
    ExperimentOutcome,
    ExperimentProtocol,
    ExperimentReport,
    ExperimentResult,
    ExperimentStatus,
    ExperimentValidationError,
    HypothesisRecord,
    HypothesisRegistry,
    HypothesisStatus,
    SQLiteExperimentRepository,
    ScientificExperiment,
    compute_experiment_fingerprint,
    compute_experiment_id,
    compute_hypothesis_id,
    compute_protocol_id,
    compute_result_id,
    generate_experiment_report,
)


@pytest.fixture
def temp_executor():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db_path = tmp.name
    tmp.close()

    repo = SQLiteExperimentRepository(db_path)
    hyp_reg = HypothesisRegistry()
    executor = ExperimentExecutor(hypothesis_registry=hyp_reg)
    yield executor, repo, hyp_reg, db_path

    repo.close()
    if os.path.exists(db_path):
        os.remove(db_path)


def test_experiment_protocol_and_hypothesis_identity():
    """Verify EXP_<HEX16>, EFP_<HEX64>, PROT_<HEX16>, HYP_<HEX16>, and RES_<HEX16> identities."""
    pid, p_hash = compute_protocol_id("StandardValidation", "1.0.0", ["Stage 1", "Stage 2"])
    assert pid.startswith("PROT_")
    assert len(pid) == 21
    assert len(p_hash) == 64

    hyp_id = compute_hypothesis_id("Volatility Predicts Range", "1.0.0")
    assert hyp_id.startswith("HYP_")
    assert len(hyp_id) == 20

    efp = compute_experiment_fingerprint("Exp 1", "Test volatility", hyp_id, "1.0.0")
    assert efp.startswith("EFP_")
    assert len(efp) == 68

    exp_id, e_hash = compute_experiment_id("Exp 1", efp, "1.0.0")
    assert exp_id.startswith("EXP_")
    assert len(exp_id) == 20

    res_id, r_hash = compute_result_id(exp_id, "validated", "2026-07-30T00:00:00Z")
    assert res_id.startswith("RES_")
    assert len(res_id) == 20


def test_hypothesis_registry_lifecycle(temp_executor):
    """Verify HypothesisRegistry registration, status updates, and lookup."""
    executor, _, hyp_reg, _ = temp_executor

    hyp = hyp_reg.register_hypothesis(
        title="Momentum Persistence",
        description="Past 10-bar returns predict forward 1-bar returns",
    )
    assert hyp.hypothesis_id.startswith("HYP_")
    assert hyp.status == HypothesisStatus.PROPOSED

    updated = hyp_reg.update_status(hyp.hypothesis_id, HypothesisStatus.VALIDATED)
    assert updated.status == HypothesisStatus.VALIDATED


def test_experiment_execution_and_result_creation(temp_executor):
    """Verify ExperimentExecutor protocol execution and ExperimentResult creation."""
    executor, repo, hyp_reg, _ = temp_executor

    hyp = hyp_reg.register_hypothesis(
        title="Mean Reversion",
        description="Z-score > 2 reverses within 5 bars",
    )

    protocol = executor.create_protocol("MeanReversionProtocol", ["Stage 1", "Stage 7"])
    exp = executor.create_experiment("MR Exp 1", "Test mean reversion", hyp.hypothesis_id, protocol)

    assert exp.experiment_id.startswith("EXP_")
    assert exp.status == ExperimentStatus.PROPOSED

    # Execute experiment protocol
    result = executor.execute_experiment(exp.experiment_id, protocol)
    assert result.result_id.startswith("RES_")
    assert result.outcome == ExperimentOutcome.VALIDATED

    # Verify status updated to VALIDATED
    final_exp = executor.get_experiment(exp.experiment_id)
    assert final_exp.status == ExperimentStatus.VALIDATED

    # Verify audit trail recorded
    audit_events = executor.get_audit_trail(exp.experiment_id)
    assert len(audit_events) >= 2


def test_sqlite_experiment_persistence(temp_executor):
    """Verify SQLiteExperimentRepository transactional persistence."""
    executor, repo, hyp_reg, _ = temp_executor

    hyp = hyp_reg.register_hypothesis("Test Hyp", "Test description")
    protocol = executor.create_protocol("TestProtocol", ["Stage 1"])
    exp = executor.create_experiment("Test Exp", "Test obj", hyp.hypothesis_id, protocol)
    result = executor.execute_experiment(exp.experiment_id, protocol)

    repo.save_hypothesis(hyp)
    repo.save_protocol(protocol)
    repo.save_experiment(exp)
    repo.save_result(result)

    loaded_exp = repo.get_experiment(exp.experiment_id)
    assert loaded_exp is not None
    assert loaded_exp.experiment_id == exp.experiment_id

    loaded_res = repo.get_result(result.result_id)
    assert loaded_res is not None
    assert loaded_res.result_id == result.result_id


def test_experiment_reporting(temp_executor):
    """Verify generate_experiment_report produces deterministic ExperimentReport."""
    executor, _, hyp_reg, _ = temp_executor

    hyp = hyp_reg.register_hypothesis("Report Hyp", "Report description")
    protocol = executor.create_protocol("ReportProtocol", ["Stage 1"])
    exp = executor.create_experiment("Report Exp", "Report obj", hyp.hypothesis_id, protocol)
    result = executor.execute_experiment(exp.experiment_id, protocol)

    final_exp = executor.get_experiment(exp.experiment_id)
    report = generate_experiment_report(final_exp, protocol, result)
    assert isinstance(report, ExperimentReport)
    assert report.report_id.startswith("EREP_")
    assert report.final_status == "validated"
    assert report.outcome_summary["outcome"] == "validated"
