"""
Project GOAT v0.7 — Scientific Qualification Engine

Evaluates scientific qualification of composite edges under market regimes deterministically:
- Evaluates qualification gates (QualificationGateEngine)
- Assigns QualificationState (QUALIFIED, DISQUALIFIED, CONDITIONAL_QUALIFICATION)
- Calculates overall readiness, confidence, evidence strength, reproducibility, explainability
"""

from __future__ import annotations

from typing import Any

from goat.composite.core.models import CompositeEdge, CompositeScore
from goat.qualification.core.canonical import (
    compute_canonical_sha256,
    compute_qualification_id,
)
from goat.qualification.core.enums import QualificationState
from goat.qualification.core.models import (
    GateEvaluation,
    QualificationGate,
    ScientificQualification,
)
from goat.qualification.gates.engine import QualificationGateEngine
from goat.regimes.core.models import MarketRegime


class ScientificQualificationEngine:
    """Engine for evaluating scientific qualifications deterministically."""

    def __init__(self, gate_engine: QualificationGateEngine | None = None) -> None:
        self.gate_engine = gate_engine or QualificationGateEngine()

    def evaluate_qualification(
        self,
        composite: CompositeEdge,
        score: CompositeScore | None,
        regime: MarketRegime,
        timestamp: str,
    ) -> tuple[ScientificQualification, list[GateEvaluation]]:
        """Evaluate scientific qualification of a composite edge deterministically.

        Args:
            composite: Target CompositeEdge model.
            score: Target CompositeScore model.
            regime: Target MarketRegime model.
            timestamp: ISO 8601 UTC timestamp string.

        Returns:
            Tuple of (ScientificQualification, list[GateEvaluation]).
        """
        q_id, _ = compute_qualification_id(composite.composite_id, regime.regime_id)
        gate_evals = self.gate_engine.evaluate_all_gates(q_id, composite, score, regime)

        gate_map = {g.gate_id: g for g in self.gate_engine.list_gates()}
        mandatory_failed = [
            e for e in gate_evals if not e.passed and gate_map.get(e.gate_id) and gate_map[e.gate_id].mandatory
        ]

        scores = [e.score for e in gate_evals]
        overall_readiness = round(sum(scores) / len(scores), 4) if scores else 0.0

        sci_conf = float(score.synergy_score) if score else 0.70
        ev_strength = round(min(1.0, len(composite.supporting_evidence) / 4.0), 4)
        repr_score = float(score.reproducibility_score) if score else 0.70
        expl_score = float(score.explainability_score) if score else 0.80

        state: QualificationState
        if mandatory_failed:
            state = QualificationState.DISQUALIFIED
        elif overall_readiness >= 0.70:
            state = QualificationState.QUALIFIED
        else:
            state = QualificationState.CONDITIONAL_QUALIFICATION

        payload = {
            "composite_id": composite.composite_id,
            "qualification_id": q_id,
            "regime_id": regime.regime_id,

        }
        canonical_hash = compute_canonical_sha256(payload).upper()

        qualification = ScientificQualification(
            qualification_id=q_id,
            composite_id=composite.composite_id,
            regime_id=regime.regime_id,
            evaluation_timestamp=timestamp,
            qualification_state=state,
            overall_readiness=overall_readiness,
            scientific_confidence=sci_conf,
            evidence_strength=ev_strength,
            reproducibility=repr_score,
            explainability=expl_score,
            metadata={"passed_gates_count": sum(1 for e in gate_evals if e.passed), "failed_gates_count": len(gate_evals) - sum(1 for e in gate_evals if e.passed)},
            canonical_hash=canonical_hash,
        )

        return qualification, gate_evals
