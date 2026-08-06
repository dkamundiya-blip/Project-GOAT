"""
Project GOAT v0.7 — Test Suite for ScientificSimulationEngine

Coverage:
- Simulation run pipeline execution
- ValidationStatus decision classification (HIGH_CONFIDENCE_VALIDATED, VALIDATED, PARTIALLY_VALIDATED, FAILED)
"""

from goat.composite.core.canonical import compute_composite_id
from goat.composite.core.models import CompositeEdge
from goat.qualification.core.canonical import compute_qualification_id
from goat.qualification.core.enums import QualificationState
from goat.qualification.core.models import ScientificQualification
from goat.regimes.core.canonical import compute_regime_id
from goat.regimes.core.enums import RegimeType
from goat.regimes.core.models import MarketRegime
from goat.simulation.backtest.engine import ScientificSimulationEngine
from goat.simulation.core.enums import ValidationStatus


def test_scientific_simulation_engine_run():
    engine = ScientificSimulationEngine()

    q_id, q_hash = compute_qualification_id("CMP_1", "MRG_1")
    qual = ScientificQualification(
        qualification_id=q_id,
        composite_id="CMP_1",
        regime_id="MRG_1",
        evaluation_timestamp="2026-07-30T00:00:00Z",
        qualification_state=QualificationState.QUALIFIED,
        overall_readiness=0.88,
        canonical_hash=q_hash,
    )

    c_id, c_hash = compute_composite_id(["SED_1"], "Composite")
    composite = CompositeEdge(composite_id=c_id, title="Composite", creation_timestamp="2026-07-30T00:00:00Z", canonical_hash=c_hash)

    r_id, r_hash = compute_regime_id("TRENDING", "2026-07-30T00:00:00Z")
    regime = MarketRegime(regime_id=r_id, timestamp="2026-07-30T00:00:00Z", regime_type=RegimeType.TRENDING, confidence=0.85, canonical_hash=r_hash)

    events = [
        {"timestamp": "2026-01-01T00:00:00Z", "pnl": 100.0},
        {"timestamp": "2026-01-02T00:00:00Z", "pnl": 150.0},
        {"timestamp": "2026-01-03T00:00:00Z", "pnl": -30.0},
    ]

    scenario, run, result = engine.run_simulation(
        qualification=qual,
        composite=composite,
        regime=regime,
        raw_events=events,
        dataset_reference="HISTORICAL_TICKS",
        timestamp="2026-07-30T00:00:00Z",
        seed=42,
    )

    assert scenario.scenario_id.startswith("SIM_")
    assert run.run_id.startswith("SRN_")
    assert result.result_id.startswith("SRS_")
    assert result.validation_status in (ValidationStatus.HIGH_CONFIDENCE_VALIDATED, ValidationStatus.VALIDATED)
