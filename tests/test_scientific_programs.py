"""
Project GOAT v0.7 — Step 4.8 Scientific Research Program Engine Test Suite
"""

from __future__ import annotations

import os
import tempfile
import pytest
from pydantic import ValidationError

from goat.programs import (
    MilestoneStatus,
    ProgramAuditEvent,
    ProgramContext,
    ProgramCoordinator,
    ProgramDesign,
    ProgramMilestone,
    ProgramReport,
    ProgramResult,
    ProgramStatus,
    ProgramStudyRecord,
    ProgramStudyRegistry,
    ProgramValidationError,
    SQLiteProgramRepository,
    ScientificResearchProgram,
    compute_milestone_id,
    compute_program_design_id,
    compute_program_fingerprint,
    compute_program_id,
    compute_program_result_id,
    generate_program_report,
)
from goat.studies import StudyCoordinator


@pytest.fixture
def temp_coordinator():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db_path = tmp.name
    tmp.close()

    repo = SQLiteProgramRepository(db_path)
    std_coord = StudyCoordinator()
    registry = ProgramStudyRegistry()
    coordinator = ProgramCoordinator(study_coordinator=std_coord, registry=registry)
    yield coordinator, repo, std_coord, db_path

    repo.close()
    if os.path.exists(db_path):
        os.remove(db_path)


def test_program_design_and_milestone_identity():
    """Verify PRG_<HEX16>, PFP_<HEX64>, PDES_<HEX16>, MS_<HEX16>, and PRES_<HEX16> identities."""
    did, d_hash = compute_program_design_id("Alpha Discovery", ["Milestone 1", "Milestone 2"], "1.0.0")
    assert did.startswith("PDES_")
    assert len(did) == 21
    assert len(d_hash) == 64

    ms_id = compute_milestone_id("Complete Phase I", "Phase I criteria")
    assert ms_id.startswith("MS_")
    assert len(ms_id) == 19

    pfp = compute_program_fingerprint("Program 1", "Quantitative Research", "Discover statistical alpha", "1.0.0")
    assert pfp.startswith("PFP_")
    assert len(pfp) == 68

    prg_id, p_hash = compute_program_id("Program 1", pfp, "1.0.0")
    assert prg_id.startswith("PRG_")
    assert len(prg_id) == 20

    res_id, r_hash = compute_program_result_id(prg_id, "2026-07-30T00:00:00Z")
    assert res_id.startswith("PRES_")
    assert len(res_id) == 21


def test_program_study_registry_ordering():
    """Verify ProgramStudyRegistry study registration and ordering."""
    registry = ProgramStudyRegistry()
    r1 = registry.register_study("PRG_1111", "STD_2222", execution_order=2)
    r2 = registry.register_study("PRG_1111", "STD_1111", execution_order=1)

    studies = registry.get_program_studies("PRG_1111")
    assert len(studies) == 2
    assert studies[0].study_id == "STD_1111"
    assert studies[1].study_id == "STD_2222"


def test_program_coordination_and_execution(temp_coordinator):
    """Verify ProgramCoordinator execution and ProgramResult creation."""
    coordinator, _, _, _ = temp_coordinator

    ms1 = coordinator.create_milestone("MS 1", "Complete baseline study")
    design = coordinator.create_design("Alpha Research Roadmap", ["Roadmap Item 1"], milestone_ids=[ms1.milestone_id])

    program = coordinator.create_program(
        title="Market Microstructure Program",
        domain="Quantitative Market Science",
        strategic_objective="Uncover persistent price discovery inefficiencies",
        description="Multi-year research campaign into microstructure anomalies",
        design=design,
    )
    assert program.program_id.startswith("PRG_")
    assert program.program_status == ProgramStatus.PROPOSED

    # Register studies into program
    coordinator.registry.register_study(program.program_id, "STD_1001", execution_order=1)
    coordinator.registry.register_study(program.program_id, "STD_1002", execution_order=2, dependencies=["STD_1001"])

    result = coordinator.execute_program(program.program_id)
    assert result.result_id.startswith("PRES_")
    assert len(result.study_references) == 2
    assert result.study_references == ["STD_1001", "STD_1002"]

    final_program = coordinator.get_program(program.program_id)
    assert final_program.program_status == ProgramStatus.COMPLETED

    audit_events = coordinator.get_audit_trail(program.program_id)
    assert len(audit_events) >= 2


def test_sqlite_program_persistence(temp_coordinator):
    """Verify SQLiteProgramRepository transactional persistence."""
    coordinator, repo, _, _ = temp_coordinator

    ms1 = coordinator.create_milestone("MS Persist", "Desc")
    design = coordinator.create_design("Persist Design", ["Item 1"], milestone_ids=[ms1.milestone_id])
    program = coordinator.create_program("Persist Program", "Domain", "Objective", "Desc", design)
    coordinator.registry.register_study(program.program_id, "STD_9999")
    result = coordinator.execute_program(program.program_id)

    repo.save_milestone(ms1)
    repo.save_design(design)
    repo.save_program(program)
    repo.save_result(result)

    loaded_prg = repo.get_program(program.program_id)
    assert loaded_prg is not None
    assert loaded_prg.program_id == program.program_id

    loaded_res = repo.get_result(result.result_id)
    assert loaded_res is not None
    assert loaded_res.result_id == result.result_id


def test_program_reporting(temp_coordinator):
    """Verify generate_program_report produces deterministic ProgramReport."""
    coordinator, _, _, _ = temp_coordinator

    design = coordinator.create_design("Report Design", ["Roadmap 1"])
    program = coordinator.create_program("Report Program", "Domain", "Objective", "Desc", design)
    coordinator.registry.register_study(program.program_id, "STD_8888")
    result = coordinator.execute_program(program.program_id)

    final_program = coordinator.get_program(program.program_id)
    report = generate_program_report(final_program, design, result)
    assert isinstance(report, ProgramReport)
    assert report.report_id.startswith("PREP_")
    assert report.final_status == "completed"
    assert report.study_statistics["total_executed_studies"] == 1
