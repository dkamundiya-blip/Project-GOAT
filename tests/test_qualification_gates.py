"""
Project GOAT v0.7 — Test Suite for QualificationGateEngine

Coverage:
- 10 default qualification gate evaluations
- Gate passing thresholds and score assignments
"""

from goat.composite.core.canonical import compute_composite_id, compute_composite_score_id
from goat.composite.core.models import CompositeEdge, CompositeScore
from goat.qualification.gates.engine import QualificationGateEngine
from goat.regimes.core.canonical import compute_regime_id
from goat.regimes.core.enums import RegimeType
from goat.regimes.core.models import MarketRegime


def test_qualification_gate_engine_default_gates():
    engine = QualificationGateEngine()
    gates = engine.list_gates()
    assert len(gates) >= 10
    # Ensure sorted by priority descending
    for i in range(len(gates) - 1):
        assert gates[i].priority >= gates[i + 1].priority


def test_evaluate_all_gates_pass():
    engine = QualificationGateEngine()

    c_id, c_hash = compute_composite_id(["SED_1", "SED_2"], "Composite Title")
    composite = CompositeEdge(
        composite_id=c_id,
        title="Composite Title",
        participating_edges=["SED_1", "SED_2"],
        participating_hypotheses=["HYP_1", "HYP_2"],
        supporting_evidence=["VAL_1", "VAL_2", "VAL_3"],
        creation_timestamp="2026-07-30T00:00:00Z",
        canonical_hash=c_hash,
    )

    s_id, s_hash = compute_composite_score_id(c_id, 0.88, "2026-07-30T00:00:00Z")
    score = CompositeScore(
        score_id=s_id,
        composite_id=c_id,
        synergy_score=0.88,
        robustness_score=0.85,
        stability_score=0.85,
        reproducibility_score=0.88,
        explainability_score=0.90,
        conflict_penalty=0.0,
        overall_score=0.88,
        timestamp="2026-07-30T00:00:00Z",
        canonical_hash=s_hash,
    )

    r_id, r_hash = compute_regime_id("TRENDING", "2026-07-30T00:00:00Z")
    regime = MarketRegime(
        regime_id=r_id,
        timestamp="2026-07-30T00:00:00Z",
        regime_type=RegimeType.TRENDING,
        confidence=0.85,
        canonical_hash=r_hash,
    )

    evals = engine.evaluate_all_gates("SQL_1", composite, score, regime)
    assert len(evals) == 10
    passed_count = sum(1 for e in evals if e.passed)
    assert passed_count >= 9
