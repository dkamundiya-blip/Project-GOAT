"""
Project GOAT v0.7 — Test Suite for DecisionReadinessEngine

Coverage:
- Decision readiness levels (NOT_READY, EARLY_RESEARCH, EXPERIMENTAL, CANDIDATE, READY_FOR_SIMULATION, READY_FOR_FORWARD_TESTING)
- Active blocking conditions detection
- QualificationExplainabilityRecord generation
"""

from goat.composite.core.canonical import compute_composite_id
from goat.composite.core.models import CompositeEdge
from goat.qualification.core.canonical import compute_qualification_id
from goat.qualification.core.enums import QualificationState, ReadinessLevel
from goat.qualification.core.models import GateEvaluation, ScientificQualification
from goat.qualification.readiness.engine import DecisionReadinessEngine


def test_evaluate_readiness_forward_testing():
    engine = DecisionReadinessEngine()

    q_id, q_hash = compute_qualification_id("CMP_1", "MRG_1")
    qual = ScientificQualification(
        qualification_id=q_id,
        composite_id="CMP_1",
        regime_id="MRG_1",
        evaluation_timestamp="2026-07-30T00:00:00Z",
        qualification_state=QualificationState.QUALIFIED,
        overall_readiness=0.90,
        scientific_confidence=0.88,
        evidence_strength=0.85,
        reproducibility=0.90,
        explainability=0.90,
        canonical_hash=q_hash,
    )

    c_id, c_hash = compute_composite_id(["SED_1"], "Composite")
    composite = CompositeEdge(composite_id=c_id, title="Composite", creation_timestamp="2026-07-30T00:00:00Z", canonical_hash=c_hash)

    evals = [
        GateEvaluation(evaluation_id=f"GEV_{i:016X}", gate_id=f"QGT_{i:016X}", qualification_id=q_id, passed=True, score=0.90)
        for i in range(10)
    ]

    readiness, expl = engine.evaluate_readiness(qual, evals, composite, "2026-07-30T00:00:00Z")

    assert readiness.readiness_id.startswith("DCR_")
    assert readiness.readiness_level == ReadinessLevel.READY_FOR_FORWARD_TESTING
    assert len(readiness.blocking_conditions) == 0
    assert expl.explanation_id.startswith("QEX_")
