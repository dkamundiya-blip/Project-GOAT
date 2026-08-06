"""
Project GOAT v0.9 — Dedicated Unit Tests for Evidence Reporting Generators
"""

import json
import pytest

from goat.evidence.collection.engine import EvidenceCollectionEngine
from goat.evidence.core.canonical import compute_summary_id
from goat.evidence.core.enums import EvidenceCategory, ObservationSource
from goat.evidence.core.models import EvidenceSummary
from goat.evidence.observation.engine import ScientificObservationEngine
from goat.evidence.reporting.reports import (
    generate_collection_summary_report,
    generate_evidence_report,
    generate_evidence_summary_report,
    generate_executive_report,
    generate_json_report,
    generate_observation_report,
)


@pytest.fixture
def obs_engine():
    return ScientificObservationEngine()


@pytest.fixture
def collection_engine():
    return EvidenceCollectionEngine()


def test_generate_observation_report(obs_engine: ScientificObservationEngine):
    obs = obs_engine.create_observation(
        metric_name="volatility_compression",
        metric_value=0.75,
        unit_of_measure="ratio",
        instrument="Volatility 100 Index",
    )
    report = generate_observation_report(obs)

    assert "# SCIENTIFIC OBSERVATION REPORT" in report
    assert obs.observation_id in report
    assert "volatility_compression" in report
    assert obs.instrument in report


def test_generate_evidence_report(obs_engine: ScientificObservationEngine, collection_engine: EvidenceCollectionEngine):
    obs = obs_engine.create_observation(metric_name="price_tick", metric_value=125.0)
    rec = collection_engine.compile_evidence_record(
        category=EvidenceCategory.PRICE,
        observations=[obs],
        title="Price Spike Evidence",
        description="Observed price spike on volatility index.",
        instrument="Volatility 100 Index",
    )
    report = generate_evidence_report(rec)

    assert "# EVIDENCE RECORD REPORT" in report
    assert rec.title in report
    assert rec.evidence_id in report
    assert obs.observation_id in report


def test_generate_collection_summary_report(
    obs_engine: ScientificObservationEngine,
    collection_engine: EvidenceCollectionEngine,
):
    obs = obs_engine.create_observation(metric_name="spread", metric_value=0.1)
    col = collection_engine.create_collection(
        collection_name="Tick Session Collection",
        observations=[obs],
    )
    report = generate_collection_summary_report(col)

    assert "# OBSERVATION COLLECTION REPORT" in report
    assert col.collection_name in report
    assert col.collection_id in report


def test_generate_json_report(obs_engine: ScientificObservationEngine):
    obs = obs_engine.create_observation(metric_name="liquidity_depth", metric_value=5000)
    json_str = generate_json_report(obs)
    data = json.loads(json_str)

    assert data["observation_id"] == obs.observation_id
    assert data["metric_name"] == "liquidity_depth"


def test_generate_evidence_summary_report():
    sum_id, sum_hash = compute_summary_id(total_observations=50, total_evidence_records=10)
    summary = EvidenceSummary(
        summary_id=sum_id,
        total_observations=50,
        total_evidence_records=10,
        total_collections=5,
        total_links=10,
        category_counts={"PRICE": 50},
        source_counts={"LIVE_MARKET": 50},
        timestamp="2026-08-04T12:00:00Z",
        canonical_hash=sum_hash,
    )
    report = generate_evidence_summary_report(summary)

    assert "# EVIDENCE SUBSYSTEM SUMMARY REPORT" in report
    assert summary.summary_id in report
    assert "PRICE" in report


@pytest.mark.parametrize("rec_count", range(1, 10))
def test_generate_executive_report(
    obs_engine: ScientificObservationEngine,
    collection_engine: EvidenceCollectionEngine,
    rec_count: int,
):
    records = []
    for i in range(rec_count):
        obs = obs_engine.create_observation(metric_name=f"metric_{i}", metric_value=i)
        rec = collection_engine.compile_evidence_record(
            category=EvidenceCategory.PRICE,
            observations=[obs],
            title=f"Exec Record #{i}",
        )
        records.append(rec)

    sum_id, sum_hash = compute_summary_id(total_observations=rec_count, total_evidence_records=rec_count)
    summary = EvidenceSummary(
        summary_id=sum_id,
        total_observations=rec_count,
        total_evidence_records=rec_count,
        total_collections=1,
        total_links=rec_count,
        timestamp="2026-08-04T12:00:00Z",
        canonical_hash=sum_hash,
    )

    exec_report = generate_executive_report(summary, records)
    assert "# PROJECT GOAT — EVIDENCE SUBSYSTEM EXECUTIVE REPORT" in exec_report
    assert f"Total Observations**: `{rec_count}`" in exec_report
    assert f"Exec Record #{rec_count - 1}" in exec_report
