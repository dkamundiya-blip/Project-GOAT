"""
Project GOAT v0.7 — Step 5.0 Scientific Evidence Synthesis Engine Test Suite
"""

from __future__ import annotations

import os
import tempfile
import pytest
from pydantic import ValidationError

from goat.synthesis import (
    ContradictionRecord,
    ContradictionSeverity,
    EvidenceCluster,
    EvidenceContradictionDetector,
    EvidenceReplicationEngine,
    EvidenceSynthesis,
    EvidenceSynthesisContext,
    EvidenceSynthesisEngine,
    EvidenceSynthesisReport,
    EvidenceSynthesisValidationError,
    ReplicationQuality,
    ReplicationRecord,
    SQLiteSynthesisRepository,
    compute_cluster_id,
    compute_contradiction_id,
    compute_synthesis_fingerprint,
    compute_synthesis_id,
    generate_synthesis_report,
)


@pytest.fixture
def temp_engine():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db_path = tmp.name
    tmp.close()

    repo = SQLiteSynthesisRepository(db_path)
    engine = EvidenceSynthesisEngine()
    yield engine, repo, db_path

    repo.close()
    if os.path.exists(db_path):
        os.remove(db_path)


def test_synthesis_cluster_and_contradiction_identity():
    """Verify SYN_<HEX16>, SFP_<HEX64>, CLS_<HEX16>, and CON_<HEX16> identities."""
    cid, c_hash = compute_cluster_id(["EVD_1111", "EVD_2222"])
    assert cid.startswith("CLS_")
    assert len(cid) == 20
    assert len(c_hash) == 64

    con_id, r_hash = compute_contradiction_id(["EVD_1111", "EVD_3333"], "high")
    assert con_id.startswith("CON_")
    assert len(con_id) == 20
    assert len(r_hash) == 64

    sfp = compute_synthesis_fingerprint(["EVD_1111"], ["KNW_1111"], "1.0.0")
    assert sfp.startswith("SFP_")
    assert len(sfp) == 68

    syn_id, s_hash = compute_synthesis_id(sfp, "1.0.0")
    assert syn_id.startswith("SYN_")
    assert len(syn_id) == 20


def test_evidence_cluster_creation(temp_engine):
    """Verify EvidenceCluster creation and statistics."""
    engine, _, _ = temp_engine

    cluster = engine.create_cluster(
        member_evidence_ids=["EVD_1001", "EVD_1002"],
        supporting_study_ids=["STD_1111"],
        confidence_statistics={"mean_pvalue": 0.01},
    )
    assert cluster.cluster_id.startswith("CLS_")
    assert len(cluster.member_evidence_ids) == 2
    assert cluster.replication_count == 1


def test_contradiction_detector_and_replication_engine():
    """Verify EvidenceContradictionDetector and EvidenceReplicationEngine."""
    evidence_data = [
        {"evidence_id": "EVD_001", "source_id": "FEAT_RET1", "outcome": "validated", "study_id": "STD_1"},
        {"evidence_id": "EVD_002", "source_id": "FEAT_RET1", "outcome": "validated", "study_id": "STD_2"},
        {"evidence_id": "EVD_003", "source_id": "FEAT_RET1", "outcome": "rejected", "study_id": "STD_3"},
    ]

    detector = EvidenceContradictionDetector()
    conflicts = detector.detect_contradictions(evidence_data)
    assert len(conflicts) >= 1
    assert conflicts[0].severity == ContradictionSeverity.HIGH

    rep_engine = EvidenceReplicationEngine()
    replications = rep_engine.analyze_replications(evidence_data)
    assert len(replications) >= 1
    assert replications[0].quality == ReplicationQuality.EXACT


def test_evidence_synthesis_engine_workflow(temp_engine):
    """Verify EvidenceSynthesisEngine end-to-end synthesis."""
    engine, repo, _ = temp_engine

    evidence_data = [
        {"evidence_id": "EVD_100", "source_id": "FEAT_A", "outcome": "validated", "study_id": "STD_1"},
        {"evidence_id": "EVD_101", "source_id": "FEAT_A", "outcome": "validated", "study_id": "STD_2"},
    ]

    synthesis = engine.synthesize_evidence(evidence_data, knowledge_ids=["KNW_500"])
    assert synthesis.synthesis_id.startswith("SYN_")
    assert synthesis.confidence_summary["validated_count"] == 2
    assert synthesis.replication_summary["total_replications"] == 1

    repo.save_synthesis(synthesis)
    loaded = repo.get_synthesis(synthesis.synthesis_id)
    assert loaded is not None
    assert loaded.synthesis_id == synthesis.synthesis_id


def test_synthesis_reporting(temp_engine):
    """Verify generate_synthesis_report produces deterministic EvidenceSynthesisReport."""
    engine, _, _ = temp_engine

    evidence_data = [
        {"evidence_id": "EVD_200", "source_id": "FEAT_B", "outcome": "validated"},
    ]

    synthesis = engine.synthesize_evidence(evidence_data)
    report = generate_synthesis_report(synthesis, clusters_count=1)

    assert isinstance(report, EvidenceSynthesisReport)
    assert report.report_id.startswith("SREP_")
    assert report.evidence_counts["total_evidence"] == 1
    assert report.cluster_counts["total_clusters"] == 1
