"""
Project GOAT v0.7 — Scientific Qualification Engine Coordinator

Main coordinator executing the qualification and decision readiness workflow:
1. Evaluate qualification gates for CompositeEdges under active MarketRegimes (ScientificQualificationEngine)
2. Determine decision readiness levels and blocking conditions (DecisionReadinessEngine)
3. Build QualificationExplainabilityRecords
4. Persist models to SQLite repositories
5. Generate reports
6. Replay past qualification and readiness decisions
"""

from __future__ import annotations

import sqlite3
from typing import Any

from goat.composite.core.models import CompositeEdge, CompositeScore
from goat.qualification.core.canonical import compute_qualification_report_id
from goat.qualification.core.models import (
    DecisionReadiness,
    GateEvaluation,
    QualificationExplainabilityRecord,
    ScientificQualification,
)
from goat.qualification.evaluation.engine import ScientificQualificationEngine
from goat.qualification.gates.engine import QualificationGateEngine
from goat.qualification.persistence.sqlite import (
    DecisionReadinessRepository,
    GateEvaluationRepository,
    GateRepository,
    QualificationReportRepository,
    QualificationRepository,
)
from goat.qualification.readiness.engine import DecisionReadinessEngine
from goat.qualification.reporting.reports import (
    DecisionReadinessReport,
    GateEvaluationReport,
    QualificationSummaryReport,
    ScientificQualificationReport,
    ScientificReadinessReport,
)
from goat.regimes.core.models import MarketRegime


class ScientificQualificationEngineCoordinator:
    """Main coordinator executing deterministic qualification & decision readiness workflow."""

    def __init__(self, conn: sqlite3.Connection | None = None) -> None:
        self.conn = conn or sqlite3.connect(":memory:")
        self.gate_engine = QualificationGateEngine()
        self.qualification_engine = ScientificQualificationEngine(gate_engine=self.gate_engine)
        self.readiness_engine = DecisionReadinessEngine()

        # Repositories
        self.qualification_repo = QualificationRepository(self.conn)
        self.gate_repo = GateRepository(self.conn)
        self.evaluation_repo = GateEvaluationRepository(self.conn)
        self.readiness_repo = DecisionReadinessRepository(self.conn)
        self.report_repo = QualificationReportRepository(self.conn)

        # Persist default gates
        for gate in self.gate_engine.list_gates():
            self.gate_repo.save_gate(gate)

    def execute_qualification_workflow(
        self,
        composite: CompositeEdge,
        score: CompositeScore | None,
        regime: MarketRegime,
        timestamp: str,
    ) -> tuple[ScientificQualification, DecisionReadiness, ScientificReadinessReport]:
        """Execute complete qualification, gate evaluation, and decision readiness workflow deterministically.

        Args:
            composite: Target CompositeEdge model.
            score: Target CompositeScore model.
            regime: Target MarketRegime model.
            timestamp: ISO 8601 UTC timestamp string.

        Returns:
            Tuple of (ScientificQualification, DecisionReadiness, ScientificReadinessReport).
        """
        # 1. Evaluate Scientific Qualification & Gates
        qualification, gate_evals = self.qualification_engine.evaluate_qualification(
            composite=composite,
            score=score,
            regime=regime,
            timestamp=timestamp,
        )
        self.qualification_repo.save_qualification(qualification)

        for ev in gate_evals:
            self.evaluation_repo.save_evaluation(ev)

        # 2. Evaluate Decision Readiness & Explainability
        readiness, explainability = self.readiness_engine.evaluate_readiness(
            qualification=qualification,
            gate_evals=gate_evals,
            composite=composite,
            timestamp=timestamp,
        )
        self.readiness_repo.save_readiness(readiness)
        self.readiness_repo.save_explanation(explainability)

        # 3. Generate Executive ScientificReadinessReport
        rep_id, _ = compute_qualification_report_id("ScientificReadinessReport", timestamp)
        r_level_str = readiness.readiness_level.value if hasattr(readiness.readiness_level, "value") else str(readiness.readiness_level)

        report = ScientificReadinessReport(
            report_id=rep_id,
            timestamp=timestamp,
            total_composites_qualified=1 if qualification.qualification_state.value == "QUALIFIED" or qualification.qualification_state == "QUALIFIED" else 0,
            top_readiness_level=r_level_str,
            top_readiness_score=qualification.overall_readiness,
            active_blocking_conditions_count=len(readiness.blocking_conditions),
            summary_notes=f"Composite '{composite.title}' assigned readiness level '{r_level_str}'.",
        )
        self.report_repo.save_report(rep_id, "ScientificReadinessReport", timestamp, report)

        return qualification, readiness, report

    def generate_sub_reports(
        self,
        qualification: ScientificQualification,
        gate_evals: list[GateEvaluation],
        readiness: DecisionReadiness,
        timestamp: str,
    ) -> dict[str, Any]:
        """Generate sub-reports (QualificationReport, GateReport, ReadinessReport, SummaryReport)."""
        qual_report = ScientificQualificationReport(
            report_id=f"SQR_QLF_{timestamp[:10]}",
            timestamp=timestamp,
            qualifications=[qualification],
        )
        gate_report = GateEvaluationReport(
            report_id=f"SQR_GAT_{timestamp[:10]}",
            timestamp=timestamp,
            evaluations=gate_evals,
        )
        readiness_report = DecisionReadinessReport(
            report_id=f"SQR_RDN_{timestamp[:10]}",
            timestamp=timestamp,
            readiness_records=[readiness],
        )
        summary_report = QualificationSummaryReport(
            report_id=f"SQR_SUM_{timestamp[:10]}",
            timestamp=timestamp,
            total_qualified=1 if qualification.qualification_state.value == "QUALIFIED" else 0,
            total_disqualified=1 if qualification.qualification_state.value == "DISQUALIFIED" else 0,
            total_conditional=1 if qualification.qualification_state.value == "CONDITIONAL_QUALIFICATION" else 0,
        )

        return {
            "qualification_report": qual_report,
            "gate_report": gate_report,
            "readiness_report": readiness_report,
            "summary_report": summary_report,
        }

    def replay_qualification(self, qualification_id: str) -> ScientificQualification:
        """Replay exact ScientificQualification model from persistence repository."""
        q = self.qualification_repo.get_qualification(qualification_id)
        if not q:
            raise KeyError(f"Qualification ID '{qualification_id}' not found in persistence repository.")
        return q

    def replay_readiness(self, readiness_id: str) -> DecisionReadiness:
        """Replay exact DecisionReadiness model from persistence repository."""
        r = self.readiness_repo.get_readiness(readiness_id)
        if not r:
            raise KeyError(f"Readiness ID '{readiness_id}' not found in persistence repository.")
        return r
