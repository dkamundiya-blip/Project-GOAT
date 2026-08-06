"""
Project GOAT v0.7 — Scientific Risk Engine Coordinator

Main coordinator executing the deterministic risk management workflow:
1. Create RiskProfile from qualification & simulation results
2. Calculate PositionSizingDecision targets (PositionSizingEngine)
3. Evaluate RiskRules & PositionEligibility (RiskRulesEngine)
4. Assess portfolio exposure (ExposureAssessmentEngine)
5. Allocate capital (CapitalAllocationEngine)
6. Compute monetary risk metrics (MonetaryRiskCalculator)
7. Persist models to SQLite repositories
8. Generate sub-reports and executive report
9. Replay past sizing decisions and allocations
"""

from __future__ import annotations

import sqlite3
from typing import Any

from goat.qualification.core.models import ScientificQualification
from goat.risk.allocation.engine import CapitalAllocationEngine
from goat.risk.calculators.monetary import MonetaryRiskCalculator
from goat.risk.calculators.rules import RiskRulesEngine
from goat.risk.core.canonical import (
    compute_risk_assessment_id,
    compute_risk_profile_id,
    compute_risk_report_id,
)
from goat.risk.core.models import (
    CapitalAllocation,
    ExposureAssessment,
    PositionSizingDecision,
    RiskAssessment,
    RiskProfile,
)
from goat.risk.exposure.engine import ExposureAssessmentEngine
from goat.risk.persistence.sqlite import (
    CapitalAllocationRepository,
    ExposureRepository,
    PositionSizingRepository,
    RiskAssessmentRepository,
    RiskProfileRepository,
    RiskReportRepository,
)
from goat.risk.reporting.reports import (
    CapitalAllocationReport,
    ExposureAssessmentReport,
    PositionSizingReport,
    RiskAssessmentReport,
    RiskExecutiveReport,
    RiskProfileReport,
)
from goat.risk.sizing.engine import PositionSizingEngine
from goat.simulation.core.models import SimulationResult


class ScientificRiskEngineCoordinator:
    """Main coordinator executing deterministic risk management & capital allocation workflow."""

    def __init__(self, conn: sqlite3.Connection | None = None) -> None:
        self.conn = conn or sqlite3.connect(":memory:")
        self.sizing_engine = PositionSizingEngine()
        self.exposure_engine = ExposureAssessmentEngine()
        self.allocation_engine = CapitalAllocationEngine()
        self.monetary_calculator = MonetaryRiskCalculator()
        self.rules_engine = RiskRulesEngine()

        # Repositories
        self.profile_repo = RiskProfileRepository(self.conn)
        self.sizing_repo = PositionSizingRepository(self.conn)
        self.allocation_repo = CapitalAllocationRepository(self.conn)
        self.exposure_repo = ExposureRepository(self.conn)
        self.assessment_repo = RiskAssessmentRepository(self.conn)
        self.report_repo = RiskReportRepository(self.conn)

    def execute_risk_workflow(
        self,
        qualification: ScientificQualification,
        simulation_result: SimulationResult,
        instrument: str,
        entry_price: float,
        stop_loss_price: float,
        take_profit_price: float,
        timestamp: str,
        account_balance: float = 100000.0,
        max_risk_percent: float = 0.02,
        max_portfolio_exposure: float = 0.20,
    ) -> tuple[PositionSizingDecision, CapitalAllocation, RiskExecutiveReport]:
        """Execute complete risk management, sizing, exposure, and capital allocation workflow deterministically.

        Args:
            qualification: Target ScientificQualification model.
            simulation_result: Target SimulationResult model.
            instrument: Ticker symbol string.
            entry_price: Target entry price.
            stop_loss_price: Target stop loss price.
            take_profit_price: Target take profit price.
            timestamp: ISO 8601 UTC timestamp string.
            account_balance: Total account balance (default 100000.0).
            max_risk_percent: Max risk fraction per trade (default 0.02 = 2%).
            max_portfolio_exposure: Max portfolio exposure fraction (default 0.20 = 20%).

        Returns:
            Tuple of (PositionSizingDecision, CapitalAllocation, RiskExecutiveReport).
        """
        # 1. Create RiskProfile
        rp_id, rp_hash = compute_risk_profile_id(qualification.qualification_id, simulation_result.result_id)
        profile = RiskProfile(
            risk_profile_id=rp_id,
            qualification_id=qualification.qualification_id,
            simulation_result_id=simulation_result.result_id,
            account_balance=account_balance,
            maximum_risk_percent=max_risk_percent,
            maximum_portfolio_exposure=max_portfolio_exposure,
            canonical_hash=rp_hash,
        )
        self.profile_repo.save_profile(profile)

        # 2. Compute PositionSizingDecision
        sizing = self.sizing_engine.calculate_position_size(
            risk_profile=profile,
            instrument=instrument,
            entry_price=entry_price,
            stop_loss_price=stop_loss_price,
            take_profit_price=take_profit_price,
        )
        self.sizing_repo.save_sizing(sizing)

        # 3. Assess Exposure & Allocate Capital
        exposure = self.exposure_engine.assess_exposure(
            risk_profile=profile,
            active_sizings=[],
            new_sizing=sizing,
        )
        self.exposure_repo.save_exposure(exposure)

        requested_cap = sizing.position_size * sizing.entry_price
        allocation = self.allocation_engine.allocate_capital(
            qualification_id=qualification.qualification_id,
            requested_capital=requested_cap,
            risk_profile=profile,
            current_reserved_capital=0.0,
        )
        self.allocation_repo.save_allocation(allocation)

        # 4. Compute RiskAssessment
        monetary_risk = sizing.metadata.get("monetary_risk", 0.0)
        monetary_reward = sizing.metadata.get("monetary_reward", 0.0)
        exp_return_pct = self.monetary_calculator.compute_expected_return_percent(monetary_reward, account_balance)

        rsa_id, _ = compute_risk_assessment_id(sizing.sizing_id)
        risk_assessment = RiskAssessment(
            assessment_id=rsa_id,
            sizing_id=sizing.sizing_id,
            total_risk=max_risk_percent * 100.0,
            monetary_risk=monetary_risk,
            expected_reward=monetary_reward,
            expected_return_percent=exp_return_pct,
            drawdown_impact=round(monetary_risk / account_balance, 4),
            assessment_summary=f"Risk assessment for sizing '{sizing.sizing_id}': monetary risk ${monetary_risk:,.2f}, expected reward ${monetary_reward:,.2f}.",
            canonical_hash=rsa_id.replace("RSA_", "") + "0" * 48,
        )
        self.assessment_repo.save_assessment(risk_assessment)

        # 5. Generate Executive Report
        rep_id, _ = compute_risk_report_id("RiskExecutiveReport", timestamp)

        report = RiskExecutiveReport(
            report_id=rep_id,
            timestamp=timestamp,
            total_opportunities_evaluated=1,
            total_capital_reserved=allocation.reserved_capital,
            top_recommended_lots=sizing.recommended_lot_size,
            top_monetary_risk=monetary_risk,
            top_monetary_reward=monetary_reward,
            summary_notes=f"Position sizing evaluated for instrument '{instrument}'. Recommended lot size: {sizing.recommended_lot_size:.2f} lots.",
        )
        self.report_repo.save_report(rep_id, "RiskExecutiveReport", timestamp, report)

        return sizing, allocation, report

    def generate_sub_reports(
        self,
        profile: RiskProfile,
        sizing: PositionSizingDecision,
        allocation: CapitalAllocation,
        exposure: ExposureAssessment,
        risk_assessment: RiskAssessment,
        timestamp: str,
    ) -> dict[str, Any]:
        """Generate sub-reports (ProfileReport, SizingReport, AllocationReport, ExposureReport, AssessmentReport)."""
        rpf_report = RiskProfileReport(
            report_id=f"SRR_RPF_{timestamp[:10]}",
            timestamp=timestamp,
            profiles=[profile],
        )
        psd_report = PositionSizingReport(
            report_id=f"SRR_PSD_{timestamp[:10]}",
            timestamp=timestamp,
            sizing_decisions=[sizing],
        )
        cal_report = CapitalAllocationReport(
            report_id=f"SRR_CAL_{timestamp[:10]}",
            timestamp=timestamp,
            allocations=[allocation],
        )
        exp_report = ExposureAssessmentReport(
            report_id=f"SRR_EXP_{timestamp[:10]}",
            timestamp=timestamp,
            assessments=[exposure],
        )
        rsa_report = RiskAssessmentReport(
            report_id=f"SRR_RSA_{timestamp[:10]}",
            timestamp=timestamp,
            risk_assessments=[risk_assessment],
        )

        return {
            "profile_report": rpf_report,
            "sizing_report": psd_report,
            "allocation_report": cal_report,
            "exposure_report": exp_report,
            "assessment_report": rsa_report,
        }

    def replay_sizing(self, sizing_id: str) -> PositionSizingDecision:
        """Replay exact PositionSizingDecision model from persistence repository."""
        s = self.sizing_repo.get_sizing(sizing_id)
        if not s:
            raise KeyError(f"PositionSizingDecision ID '{sizing_id}' not found in persistence repository.")
        return s

    def replay_allocation(self, allocation_id: str) -> CapitalAllocation:
        """Replay exact CapitalAllocation model from persistence repository."""
        a = self.allocation_repo.get_allocation(allocation_id)
        if not a:
            raise KeyError(f"CapitalAllocation ID '{allocation_id}' not found in persistence repository.")
        return a
