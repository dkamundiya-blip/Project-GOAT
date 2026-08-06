"""
Project GOAT v0.7 — Step 4.7 Scientific Research Study Engine Test Suite
"""

from __future__ import annotations

import os
import tempfile
import pytest
from pydantic import ValidationError

from goat.experiments import (
    ExperimentExecutor,
    HypothesisRegistry,
)
from goat.studies import (
    SQLiteStudyRepository,
    ScientificStudy,
    StudyAuditEvent,
    StudyContext,
    StudyCoordinator,
    StudyDesign,
    StudyExperimentRecord,
    StudyExperimentRegistry,
    StudyReport,
    StudyResult,
    StudyStatus,
    StudyValidationError,
    compute_design_id,
    compute_study_fingerprint,
    compute_study_id,
    compute_study_result_id,
    generate_study_report,
)


@pytest.fixture
def temp_coordinator():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db_path = tmp.name
    tmp.close()

    repo = SQLiteStudyRepository(db_path)
    hyp_reg = HypothesisRegistry()
    exp_exec = ExperimentExecutor(hypothesis_registry=hyp_reg)
    exp_reg = StudyExperimentRegistry()
    coordinator = StudyCoordinator(experiment_executor=exp_exec, registry=exp_reg)
    yield coordinator, repo, exp_exec, hyp_reg, db_path

    repo.close()
    if os.path.exists(db_path):
        os.remove(db_path)


def test_study_and_design_identity():
    """Verify STD_<HEX16>, SFP_<HEX64>, DES_<HEX16>, and SRES_<HEX16> identities."""
    did, d_hash = compute_design_id("Volatility Study", ["Exp 1", "Exp 2"], "1.0.0")
    assert did.startswith("DES_")
    assert len(did) == 20
    assert len(d_hash) == 64

    sfp = compute_study_fingerprint("Study 1", "Does volatility decay?", "Investigate decay", "1.0.0")
    assert sfp.startswith("SFP_")
    assert len(sfp) == 68

    std_id, s_hash = compute_study_id("Study 1", sfp, "1.0.0")
    assert std_id.startswith("STD_")
    assert len(std_id) == 20

    res_id, r_hash = compute_study_result_id(std_id, "2026-07-30T00:00:00Z")
    assert res_id.startswith("SRES_")
    assert len(res_id) == 21


def test_study_experiment_registry_ordering():
    """Verify StudyExperimentRegistry experiment registration and ordering."""
    registry = StudyExperimentRegistry()
    r1 = registry.register_experiment("STD_1111", "EXP_2222", execution_order=2)
    r2 = registry.register_experiment("STD_1111", "EXP_1111", execution_order=1)

    exps = registry.get_study_experiments("STD_1111")
    assert len(exps) == 2
    assert exps[0].experiment_id == "EXP_1111"
    assert exps[1].experiment_id == "EXP_2222"


def test_study_coordination_and_execution(temp_coordinator):
    """Verify StudyCoordinator execution and StudyResult creation."""
    coordinator, _, exp_exec, hyp_reg, _ = temp_coordinator

    design = coordinator.create_design("Volatility Decay Study", ["Exp 1", "Exp 2"])
    study = coordinator.create_study(
        title="Volatility Clustering Study",
        scientific_question="Is volatility clustering persistent across regimes?",
        research_objective="Evaluate multi-regime volatility persistence",
        description="Comprehensive study of volatility decay",
        design=design,
    )
    assert study.study_id.startswith("STD_")
    assert study.status == StudyStatus.PROPOSED

    # Register experiments into study
    coordinator.registry.register_experiment(study.study_id, "EXP_1001", execution_order=1)
    coordinator.registry.register_experiment(study.study_id, "EXP_1002", execution_order=2, dependencies=["EXP_1001"])

    result = coordinator.execute_study(study.study_id)
    assert result.result_id.startswith("SRES_")
    assert len(result.experiment_references) == 2
    assert result.experiment_references == ["EXP_1001", "EXP_1002"]

    final_study = coordinator.get_study(study.study_id)
    assert final_study.status == StudyStatus.COMPLETED

    audit_events = coordinator.get_audit_trail(study.study_id)
    assert len(audit_events) >= 2


def test_sqlite_study_persistence(temp_coordinator):
    """Verify SQLiteStudyRepository transactional persistence."""
    coordinator, repo, _, _, _ = temp_coordinator

    design = coordinator.create_design("Persistence Design", ["Exp 1"])
    study = coordinator.create_study("Persist Study", "Question?", "Objective", "Desc", design)
    coordinator.registry.register_experiment(study.study_id, "EXP_9999")
    result = coordinator.execute_study(study.study_id)

    repo.save_design(design)
    repo.save_study(study)
    repo.save_result(result)

    loaded_study = repo.get_study(study.study_id)
    assert loaded_study is not None
    assert loaded_study.study_id == study.study_id

    loaded_res = repo.get_result(result.result_id)
    assert loaded_res is not None
    assert loaded_res.result_id == result.result_id


def test_study_reporting(temp_coordinator):
    """Verify generate_study_report produces deterministic StudyReport."""
    coordinator, _, _, _, _ = temp_coordinator

    design = coordinator.create_design("Report Design", ["Exp 1"])
    study = coordinator.create_study("Report Study", "Q?", "Obj", "Desc", design)
    coordinator.registry.register_experiment(study.study_id, "EXP_8888")
    result = coordinator.execute_study(study.study_id)

    final_study = coordinator.get_study(study.study_id)
    report = generate_study_report(final_study, design, result)
    assert isinstance(report, StudyReport)
    assert report.report_id.startswith("SREP_")
    assert report.final_status == "completed"
    assert report.experiment_statistics["total_executed_experiments"] == 1
