"""
Project GOAT v0.9 — Dedicated Unit Tests for Master Statistical Engine Facade
"""

import pytest

from goat.statistics.core.enums import ScientificDecision
from goat.statistics.engine import MasterStatisticalEngine
from goat.statistics.persistence.sqlite import StatisticalPersistenceContext


@pytest.fixture
def memory_context():
    ctx = StatisticalPersistenceContext(db_path=":memory:")
    yield ctx
    ctx.close()


@pytest.fixture
def master_engine(memory_context):
    return MasterStatisticalEngine(persistence_context=memory_context)


@pytest.mark.parametrize("idx", range(1, 10))
def test_master_engine_evaluate_and_persist(master_engine: MasterStatisticalEngine, idx: int):
    exp_id = f"EXP_{idx:016X}"
    hyp_id = f"HYP_{idx:016X}"
    samples = [0.4 + idx * 0.1] * 120

    ev, dec, conf, sig, exp = master_engine.evaluate_experiment(
        experiment_id=exp_id,
        hypothesis_id=hyp_id,
        samples=samples,
    )

    assert ev.evaluation_id.startswith("STE_")
    assert dec.decision_id.startswith("EVD_")
    assert dec.decision == ScientificDecision.SUPPORTED
    assert master_engine.persistence is not None

    fetched_ev = master_engine.persistence.evaluations.get_by_id(ev.evaluation_id)
    assert fetched_ev is not None
    assert fetched_ev.evaluation_id == ev.evaluation_id

    fetched_dec = master_engine.persistence.decisions.get_by_id(dec.decision_id)
    assert fetched_dec is not None


def test_master_engine_report_generation(master_engine: MasterStatisticalEngine):
    samples = [0.8] * 150
    ev, _, _, _, _ = master_engine.evaluate_experiment(
        experiment_id="EXP_1234567890ABCDEF",
        hypothesis_id="HYP_1234567890ABCDEF",
        samples=samples,
    )

    reports = master_engine.generate_reports(ev.evaluation_id)
    assert "statistical" in reports
    assert "executive" in reports
    assert "json" in reports
    assert "confidence" in reports
    assert "significance" in reports
    assert "expectancy" in reports
    assert ev.evaluation_id in reports["statistical"]
