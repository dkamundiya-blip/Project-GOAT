"""
Project GOAT v0.7 — Step 4.9 Scientific Research Portfolio Engine Test Suite
"""

from __future__ import annotations

import os
import tempfile
import pytest
from pydantic import ValidationError

from goat.portfolios import (
    PortfolioAuditEvent,
    PortfolioContext,
    PortfolioCoordinator,
    PortfolioDesign,
    PortfolioGovernancePolicy,
    PortfolioProgramRecord,
    PortfolioProgramRegistry,
    PortfolioReport,
    PortfolioResult,
    PortfolioStatus,
    PortfolioValidationError,
    SQLitePortfolioRepository,
    ScientificResearchPortfolio,
    compute_governance_policy_id,
    compute_portfolio_design_id,
    compute_portfolio_fingerprint,
    compute_portfolio_id,
    compute_portfolio_result_id,
    generate_portfolio_report,
)
from goat.programs import ProgramCoordinator


@pytest.fixture
def temp_coordinator():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db_path = tmp.name
    tmp.close()

    repo = SQLitePortfolioRepository(db_path)
    prg_coord = ProgramCoordinator()
    registry = PortfolioProgramRegistry()
    coordinator = PortfolioCoordinator(program_coordinator=prg_coord, registry=registry)
    yield coordinator, repo, prg_coord, db_path

    repo.close()
    if os.path.exists(db_path):
        os.remove(db_path)


def test_portfolio_design_and_governance_identity():
    """Verify PFO_<HEX16>, PFFP_<HEX64>, PFD_<HEX16>, GOV_<HEX16>, and PFR_<HEX16> identities."""
    gid, g_hash = compute_governance_policy_id("StandardGovernance", "quarterly")
    assert gid.startswith("GOV_")
    assert len(gid) == 20
    assert len(g_hash) == 64

    did, d_hash = compute_portfolio_design_id("Master Research Roadmap", "1.0.0")
    assert did.startswith("PFD_")
    assert len(did) == 20
    assert len(d_hash) == 64

    pffp = compute_portfolio_fingerprint("Global Portfolio", "GOAT Inst", "Systematic Alpha", "1.0.0")
    assert pffp.startswith("PFFP_")
    assert len(pffp) == 69

    pfo_id, p_hash = compute_portfolio_id("Global Portfolio", pffp, "1.0.0")
    assert pfo_id.startswith("PFO_")
    assert len(pfo_id) == 20

    res_id, r_hash = compute_portfolio_result_id(pfo_id, "2026-07-30T00:00:00Z")
    assert res_id.startswith("PFR_")
    assert len(res_id) == 20


def test_portfolio_program_registry_ordering():
    """Verify PortfolioProgramRegistry program registration and ordering."""
    registry = PortfolioProgramRegistry()
    r1 = registry.register_program("PFO_1111", "PRG_2222", execution_order=2)
    r2 = registry.register_program("PFO_1111", "PRG_1111", execution_order=1)

    programs = registry.get_portfolio_programs("PFO_1111")
    assert len(programs) == 2
    assert programs[0].program_id == "PRG_1111"
    assert programs[1].program_id == "PRG_2222"


def test_portfolio_coordination_and_execution(temp_coordinator):
    """Verify PortfolioCoordinator execution and PortfolioResult creation."""
    coordinator, _, _, _ = temp_coordinator

    gov = coordinator.create_governance_policy("Alpha Policy", "quarterly")
    design = coordinator.create_design("Alpha Strategic Roadmap", governance_policy_id=gov.policy_id)

    portfolio = coordinator.create_portfolio(
        title="Global Quantitative Research Portfolio",
        organization="Project GOAT Research Foundation",
        vision="Systematic scientific edge discovery across synthetic markets",
        description="Master portfolio governing all scientific research initiatives",
        design=design,
    )
    assert portfolio.portfolio_id.startswith("PFO_")
    assert portfolio.portfolio_status == PortfolioStatus.PROPOSED

    # Register programs into portfolio
    coordinator.registry.register_program(portfolio.portfolio_id, "PRG_1001", execution_order=1)
    coordinator.registry.register_program(portfolio.portfolio_id, "PRG_1002", execution_order=2, dependencies=["PRG_1001"])

    result = coordinator.execute_portfolio(portfolio.portfolio_id)
    assert result.result_id.startswith("PFR_")
    assert len(result.program_references) == 2
    assert result.program_references == ["PRG_1001", "PRG_1002"]

    final_portfolio = coordinator.get_portfolio(portfolio.portfolio_id)
    assert final_portfolio.portfolio_status == PortfolioStatus.COMPLETED

    audit_events = coordinator.get_audit_trail(portfolio.portfolio_id)
    assert len(audit_events) >= 2


def test_sqlite_portfolio_persistence(temp_coordinator):
    """Verify SQLitePortfolioRepository transactional persistence."""
    coordinator, repo, _, _ = temp_coordinator

    gov = coordinator.create_governance_policy("Persist Gov")
    design = coordinator.create_design("Persist PFD", governance_policy_id=gov.policy_id)
    portfolio = coordinator.create_portfolio("Persist PFO", "Org", "Vision", "Desc", design)
    coordinator.registry.register_program(portfolio.portfolio_id, "PRG_9999")
    result = coordinator.execute_portfolio(portfolio.portfolio_id)

    repo.save_governance_policy(gov)
    repo.save_design(design)
    repo.save_portfolio(portfolio)
    repo.save_result(result)

    loaded_pfo = repo.get_portfolio(portfolio.portfolio_id)
    assert loaded_pfo is not None
    assert loaded_pfo.portfolio_id == portfolio.portfolio_id

    loaded_res = repo.get_result(result.result_id)
    assert loaded_res is not None
    assert loaded_res.result_id == result.result_id


def test_portfolio_reporting(temp_coordinator):
    """Verify generate_portfolio_report produces deterministic PortfolioReport."""
    coordinator, _, _, _ = temp_coordinator

    gov = coordinator.create_governance_policy("Report Gov")
    design = coordinator.create_design("Report PFD", governance_policy_id=gov.policy_id)
    portfolio = coordinator.create_portfolio("Report PFO", "Org", "Vision", "Desc", design)
    coordinator.registry.register_program(portfolio.portfolio_id, "PRG_8888")
    result = coordinator.execute_portfolio(portfolio.portfolio_id)

    final_portfolio = coordinator.get_portfolio(portfolio.portfolio_id)
    report = generate_portfolio_report(final_portfolio, design, gov, result)
    assert isinstance(report, PortfolioReport)
    assert report.report_id.startswith("PREP_")
    assert report.final_status == "completed"
    assert report.program_statistics["total_executed_programs"] == 1
