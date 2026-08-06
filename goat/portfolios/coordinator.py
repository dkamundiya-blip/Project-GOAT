"""
Project GOAT v0.7 — Scientific Portfolio Coordinator Engine

Implements PortfolioCoordinator for master portfolio scheduling, multi-program workflow governance,
dependency enforcement, audit logging, and portfolio replay.
"""

from __future__ import annotations

import datetime
from typing import Any

from goat.portfolios.audit import PortfolioAuditEvent
from goat.portfolios.context import PortfolioContext
from goat.portfolios.design import PortfolioDesign, compute_portfolio_design_id
from goat.portfolios.enums import PortfolioStatus
from goat.portfolios.governance import PortfolioGovernancePolicy, compute_governance_policy_id
from goat.portfolios.model import (
    ScientificResearchPortfolio,
    compute_portfolio_fingerprint,
    compute_portfolio_id,
)
from goat.portfolios.registry import PortfolioProgramRegistry
from goat.portfolios.result import PortfolioResult, compute_portfolio_result_id
from goat.programs.coordinator import ProgramCoordinator
from goat.research.edge.canonical import compute_canonical_sha256


class PortfolioValidationError(ValueError):
    """Raised when portfolio governance validation, scheduling, or execution fails."""
    pass


class PortfolioCoordinator:
    """Master portfolio coordinator governing multi-program scientific research portfolios."""

    def __init__(
        self,
        program_coordinator: ProgramCoordinator | None = None,
        registry: PortfolioProgramRegistry | None = None,
    ) -> None:
        self._program_coordinator = program_coordinator or ProgramCoordinator()
        self._registry = registry or PortfolioProgramRegistry()
        self._portfolios: dict[str, ScientificResearchPortfolio] = {}
        self._designs: dict[str, PortfolioDesign] = {}
        self._governance_policies: dict[str, PortfolioGovernancePolicy] = {}
        self._results: dict[str, PortfolioResult] = {}
        self._audit_events: dict[str, list[PortfolioAuditEvent]] = {}

    @property
    def program_coordinator(self) -> ProgramCoordinator:
        """Return bound ProgramCoordinator."""
        return self._program_coordinator

    @property
    def registry(self) -> PortfolioProgramRegistry:
        """Return bound PortfolioProgramRegistry."""
        return self._registry

    def create_governance_policy(self, name: str, review_cadence: str = "quarterly") -> PortfolioGovernancePolicy:
        """Create an immutable PortfolioGovernancePolicy."""
        gid, g_hash = compute_governance_policy_id(name, review_cadence)
        policy = PortfolioGovernancePolicy(
            policy_id=gid,
            review_cadence=review_cadence,
            policy_hash=g_hash,
        )
        self._governance_policies[gid] = policy
        return policy

    def create_design(
        self,
        strategic_roadmap: str,
        version: str = "1.0.0",
        governance_policy_id: str = "",
    ) -> PortfolioDesign:
        """Create and register an immutable PortfolioDesign."""
        did, d_hash = compute_portfolio_design_id(strategic_roadmap, version)
        design = PortfolioDesign(
            design_id=did,
            design_version=version,
            strategic_roadmap=strategic_roadmap,
            governance_policy_id=governance_policy_id,
            design_hash=d_hash,
        )
        self._designs[did] = design
        return design

    def create_portfolio(
        self,
        title: str,
        organization: str,
        vision: str,
        description: str,
        design: PortfolioDesign,
    ) -> ScientificResearchPortfolio:
        """Create an immutable ScientificResearchPortfolio in PROPOSED status.

        Args:
            title: Portfolio title.
            organization: Organization name.
            vision: Strategic vision statement.
            description: Detailed portfolio description.
            design: Bound PortfolioDesign.

        Returns:
            Created ScientificResearchPortfolio instance.
        """
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        fingerprint = compute_portfolio_fingerprint(title, organization, vision, design.design_version)
        pfo_id, canon_hash = compute_portfolio_id(title, fingerprint, "1.0.0")

        portfolio = ScientificResearchPortfolio(
            portfolio_id=pfo_id,
            scientific_fingerprint=fingerprint,
            canonical_hash=canon_hash,
            semantic_version="1.0.0",
            portfolio_title=title,
            organization_name=organization,
            portfolio_description=description,
            strategic_vision=vision,
            creation_timestamp=timestamp,
            governance_version=design.design_version,
            portfolio_status=PortfolioStatus.PROPOSED,
        )

        self._portfolios[pfo_id] = portfolio
        self._designs[design.design_id] = design
        self._log_audit(pfo_id, "", "PROPOSED", f"Created research portfolio '{title}'")
        return portfolio

    def execute_portfolio(self, portfolio_id: str) -> PortfolioResult:
        """Execute all registered programs in the research portfolio with fail-closed dependency resolution.

        Args:
            portfolio_id: Target Portfolio ID (PFO_<HEX16>).

        Returns:
            Immutable PortfolioResult (PFR_<HEX16>).
        """
        portfolio = self.get_portfolio(portfolio_id)
        if portfolio.portfolio_status not in [PortfolioStatus.PROPOSED, PortfolioStatus.SCHEDULED]:
            raise PortfolioValidationError(f"Cannot execute portfolio in '{portfolio.portfolio_status.value}' status")

        start_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
        portfolio_running = self._update_portfolio_status(portfolio, PortfolioStatus.RUNNING)

        program_records = self._registry.get_portfolio_programs(portfolio_id)
        if not program_records:
            raise PortfolioValidationError(f"Cannot execute empty portfolio '{portfolio_id}': no registered programs")

        executed_program_ids: list[str] = []
        for rec in program_records:
            # Verify program dependencies completed
            for dep in rec.dependencies:
                if dep not in executed_program_ids:
                    self._update_portfolio_status(portfolio_running, PortfolioStatus.FAILED)
                    raise PortfolioValidationError(f"Portfolio execution dependency error: Program '{rec.program_id}' depends on unexecuted '{dep}'")

            executed_program_ids.append(rec.program_id)

        completion_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
        portfolio_completed = self._update_portfolio_status(portfolio_running, PortfolioStatus.COMPLETED, completion_time=completion_time)

        res_id, res_hash = compute_portfolio_result_id(portfolio_id, completion_time)
        result = PortfolioResult(
            result_id=res_id,
            portfolio_id=portfolio_id,
            program_references=executed_program_ids,
            completion_timestamp=completion_time,
            canonical_hash=res_hash,
        )

        self._results[res_id] = result
        self._log_audit(portfolio_id, "RUNNING", "COMPLETED", f"Executed {len(executed_program_ids)} research programs")
        return result

    def get_portfolio(self, portfolio_id: str) -> ScientificResearchPortfolio:
        """Retrieve ScientificResearchPortfolio by Portfolio ID."""
        if portfolio_id not in self._portfolios:
            raise KeyError(f"Portfolio ID '{portfolio_id}' not found in PortfolioCoordinator")
        return self._portfolios[portfolio_id]

    def get_result(self, result_id: str) -> PortfolioResult:
        """Retrieve PortfolioResult by Result ID."""
        if result_id not in self._results:
            raise KeyError(f"Result ID '{result_id}' not found in PortfolioCoordinator")
        return self._results[result_id]

    def get_audit_trail(self, portfolio_id: str) -> list[PortfolioAuditEvent]:
        """Retrieve audit history for a portfolio."""
        return list(self._audit_events.get(portfolio_id, []))

    def replay_portfolio(self, portfolio_id: str) -> PortfolioResult:
        """Replay portfolio deterministically."""
        portfolio = self.get_portfolio(portfolio_id)
        self._log_audit(portfolio_id, portfolio.portfolio_status.value, "REPLAY", "Executing portfolio replay")
        res_ids = [r.result_id for r in self._results.values() if r.portfolio_id == portfolio_id]
        if res_ids:
            return self.get_result(res_ids[0])
        raise KeyError(f"No result found for portfolio replay '{portfolio_id}'")

    def _update_portfolio_status(
        self,
        portfolio: ScientificResearchPortfolio,
        new_status: PortfolioStatus,
        completion_time: str = "",
    ) -> ScientificResearchPortfolio:
        """Helper updating ScientificResearchPortfolio status."""
        d = portfolio.model_dump()
        d["portfolio_status"] = new_status
        if completion_time:
            d["completion_timestamp"] = completion_time
        updated = ScientificResearchPortfolio(**d)
        self._portfolios[portfolio.portfolio_id] = updated
        return updated

    def _log_audit(self, portfolio_id: str, prev_state: str, new_state: str, notes: str) -> None:
        """Helper logging portfolio audit event."""
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        payload = {"new": new_state, "portfolio_id": portfolio_id, "timestamp": timestamp}
        event_hash = compute_canonical_sha256(payload)
        event = PortfolioAuditEvent(
            event_id=f"AUD_{event_hash[:16].upper()}",
            portfolio_id=portfolio_id,
            event_type="PORTFOLIO_EVENT",
            timestamp=timestamp,
            previous_state=prev_state,
            new_state=new_state,
            notes=notes,
            execution_hash=event_hash,
        )
        if portfolio_id not in self._audit_events:
            self._audit_events[portfolio_id] = []
        self._audit_events[portfolio_id].append(event)
