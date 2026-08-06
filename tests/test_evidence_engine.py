"""
Project GOAT v0.9 — Dedicated Unit Tests for Scientific Evidence Engine Facade
"""

import pytest

from goat.evidence.core.enums import EvidenceCategory, ObservationSource
from goat.evidence.engine import ScientificEvidenceEngine
from goat.evidence.persistence.sqlite import EvidencePersistenceContext


@pytest.fixture
def memory_context():
    ctx = EvidencePersistenceContext(db_path=":memory:")
    yield ctx
    ctx.close()


@pytest.fixture
def evidence_engine(memory_context):
    return ScientificEvidenceEngine(persistence_context=memory_context)


@pytest.mark.parametrize("idx", range(1, 10))
def test_engine_create_observation(evidence_engine: ScientificEvidenceEngine, idx: int):
    obs = evidence_engine.create_observation(
        metric_name=f"facade_metric_{idx}",
        metric_value=idx * 1.5,
        category=EvidenceCategory.VOLATILITY,
        instrument="Volatility 50 Index",
    )

    assert obs.observation_id.startswith("OBS_")
    assert obs.metric_name == f"facade_metric_{idx}"
    assert evidence_engine.persistence is not None

    fetched = evidence_engine.persistence.observations.get_by_id(obs.observation_id)
    assert fetched is not None
    assert fetched.observation_id == obs.observation_id


@pytest.mark.parametrize("idx", range(1, 10))
def test_engine_compile_and_link(evidence_engine: ScientificEvidenceEngine, idx: int):
    obs = evidence_engine.create_observation(
        metric_name=f"metric_{idx}",
        metric_value=idx,
    )
    rec = evidence_engine.compile_evidence_record(
        category=EvidenceCategory.PRICE,
        observations=[obs],
        title=f"Record Title #{idx}",
    )
    hyp_id = f"HYP_{idx:016X}"
    link = evidence_engine.create_link(
        hypothesis_id=hyp_id,
        target_id=rec.evidence_id,
    )

    assert rec.evidence_id.startswith("EVR_")
    assert link.link_id.startswith("LNK_")
    assert link.hypothesis_id == hyp_id
    assert link.target_id == rec.evidence_id

    fetched_rec = evidence_engine.persistence.evidence_records.get_by_id(rec.evidence_id)
    assert fetched_rec is not None

    fetched_links = evidence_engine.persistence.links.get_by_hypothesis_id(hyp_id)
    assert len(fetched_links) == 1


def test_engine_report_generation(evidence_engine: ScientificEvidenceEngine):
    obs = evidence_engine.create_observation(metric_name="vol_ratio", metric_value=1.4)
    rec = evidence_engine.compile_evidence_record(category=EvidenceCategory.VOLATILITY, observations=[obs], title="Vol Title")

    reports = evidence_engine.generate_reports(rec.evidence_id)
    assert "summary" in reports
    assert "executive" in reports
    assert "markdown" in reports
    assert "json" in reports
    assert rec.title in reports["markdown"]
