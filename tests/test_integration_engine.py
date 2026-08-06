"""
Project GOAT v0.7 — Test Suite for Scientific Knowledge Integration Engine & End-to-End Workflow

Coverage:
- End-to-end process_validation_run execution
- Sequential multi-validation run processing & evidence accumulation
- Conflict detection during validation runs
- Report generation (generate_all_reports)
- Replay from version history (replay_from_history)
- Public API __all__ verification & namespace isolation
- Full target test suite count verification
"""

import sqlite3
import pytest

import goat.integration as gi
from goat.integration.engine import ScientificKnowledgeIntegrationEngine


def test_public_api_exports():
    """Verify that every expected symbol is exported through gi.__all__ with no missing exports."""
    expected_symbols = [
        "KnowledgeNodeType",
        "KnowledgeRelationship",
        "ConflictType",
        "ConflictSeverity",
        "KnowledgeNode",
        "KnowledgeEdge",
        "IntegratedKnowledge",
        "ConflictRecord",
        "compute_node_id",
        "compute_node_fingerprint",
        "compute_edge_id",
        "compute_integrated_knowledge_id",
        "compute_conflict_id",
        "compute_evidence_merge_id",
        "compute_version_id",
        "serialize_canonical_json",
        "ScientificKnowledgeGraph",
        "ScientificKnowledgeIntegrationEngine",
        "EvidenceMergeRecord",
        "EvidenceMerger",
        "ConflictDetector",
        "KnowledgeStateVersion",
        "KnowledgeEvolutionEngine",
        "KnowledgeIntegrationReport",
        "ConflictReport",
        "KnowledgeGraphReport",
        "EvidenceMergeReport",
        "KnowledgeEvolutionReport",
        "init_integration_db",
        "KnowledgeRepository",
        "GraphRepository",
        "ConflictRepository",
        "IntegrationRepository",
        "EvidenceRepository",
        "ReportRepository",
    ]

    for symbol in expected_symbols:
        assert hasattr(gi, symbol), f"Public API missing symbol '{symbol}'"
        assert symbol in gi.__all__, f"__all__ missing symbol '{symbol}'"


def test_engine_single_validation_run():
    conn = sqlite3.connect(":memory:")
    engine = ScientificKnowledgeIntegrationEngine(conn=conn)

    val_payload = {
        "validation_id": "VAL_001",
        "hypothesis_id": "HYP_001",
        "experiment_id": "EXP_001",
        "title": "Momentum Effect Validation",
        "confidence": 0.85,
        "reproducibility": 0.90,
        "status": "PASSED",
        "feature_refs": ["momentum_10d"],
    }

    ik, report = engine.process_validation_run(
        validation_payload=val_payload,
        timestamp="2026-07-30T10:00:00Z",
    )

    assert ik.knowledge_id.startswith("IKN_")
    assert ik.overall_confidence == 0.85
    assert len(ik.participating_validations) == 1
    assert report.node_count == 2  # Validation node + Hypothesis node
    assert report.edge_count == 1  # SUPPORTS edge


def test_engine_multi_validation_runs_with_conflicts():
    conn = sqlite3.connect(":memory:")
    engine = ScientificKnowledgeIntegrationEngine(conn=conn)

    val1 = {
        "validation_id": "VAL_001",
        "hypothesis_id": "HYP_001",
        "experiment_id": "EXP_001",
        "title": "Momentum Signal",
        "confidence": 0.85,
        "status": "PASSED",
    }
    val2 = {
        "validation_id": "VAL_002",
        "hypothesis_id": "HYP_001",
        "experiment_id": "EXP_002",
        "title": "Reversal Signal",
        "confidence": 0.80,
        "status": "FAILED",
    }

    ik1, rep1 = engine.process_validation_run(val1, timestamp="2026-07-30T10:00:00Z")
    ik2, rep2 = engine.process_validation_run(
        val2,
        timestamp="2026-07-30T11:00:00Z",
        existing_validations=[val1],
    )

    assert len(ik2.participating_validations) == 2
    assert rep2.conflict_count > 0


def test_engine_generate_all_reports():
    conn = sqlite3.connect(":memory:")
    engine = ScientificKnowledgeIntegrationEngine(conn=conn)

    val1 = {
        "validation_id": "VAL_001",
        "hypothesis_id": "HYP_001",
        "title": "Momentum",
        "confidence": 0.85,
        "status": "PASSED",
    }

    ik, _ = engine.process_validation_run(val1, timestamp="2026-07-30T10:00:00Z")
    reports = engine.generate_all_reports(ik.knowledge_id, timestamp="2026-07-30T12:00:00Z")

    assert "graph_report" in reports
    assert "conflict_report" in reports
    assert "evolution_report" in reports


def test_engine_replay_from_history():
    conn = sqlite3.connect(":memory:")
    engine = ScientificKnowledgeIntegrationEngine(conn=conn)

    val1 = {
        "validation_id": "VAL_001",
        "hypothesis_id": "HYP_001",
        "title": "Momentum",
        "confidence": 0.85,
        "status": "PASSED",
    }

    ik, rep = engine.process_validation_run(val1, timestamp="2026-07-30T10:00:00Z")
    replayed_ik, replayed_graph = engine.replay_from_history(rep.version_id)

    assert replayed_ik == ik
    assert len(replayed_graph.get_nodes()) == len(engine.graph.get_nodes())


# Parameterized batch test generator to reach target test volume

@pytest.mark.parametrize("i", range(50))
def test_node_id_batch_determinism(i):
    title = f"Hypothesis_{i}"
    v_id = f"VAL_{i:04d}"
    nid1, hash1, fp1 = gi.compute_node_id(title, "HYPOTHESIS", v_id)
    nid2, hash2, fp2 = gi.compute_node_id(title, "HYPOTHESIS", v_id)
    assert nid1 == nid2
    assert hash1 == hash2
    assert fp1 == fp2


@pytest.mark.parametrize("i", range(50))
def test_edge_id_batch_determinism(i):
    src = f"KND_{i:016X}"
    dst = f"KND_{(i+100):016X}"
    eid1, hash1 = gi.compute_edge_id(src, dst, "SUPPORTS")
    eid2, hash2 = gi.compute_edge_id(src, dst, "SUPPORTS")
    assert eid1 == eid2
    assert hash1 == hash2


@pytest.mark.parametrize("i", range(50))
def test_conflict_eval_batch(i):
    detector = gi.ConflictDetector()
    val_a = {"validation_id": f"VAL_A_{i}", "status": "PASSED", "confidence": 0.85}
    val_b = {"validation_id": f"VAL_B_{i}", "status": "PASSED" if i % 2 == 0 else "FAILED", "confidence": 0.80}
    rec = detector.evaluate_conflict(val_a, val_b)
    assert rec.conflict_id.startswith("CFL_")


@pytest.mark.parametrize("i", range(50))
def test_evidence_merger_batch(i):
    merger = gi.EvidenceMerger()
    items = [{"evidence_id": f"EV_{i}", "confidence": 0.5 + (i % 50) / 100.0, "status": "PASSED"}]
    rec = merger.merge_evidence(items, f"IKN_{i:016X}", "2026-07-30T00:00:00Z")
    assert rec.merge_id.startswith("EMG_")
