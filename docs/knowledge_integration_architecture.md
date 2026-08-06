# Project GOAT — Scientific Knowledge Integration & Evidence Graph Architecture

Version: v0.7 — Step 5.8  
Status: Active Implementation / Certified  
Package: `goat.integration`  

---

## 1. Architecture Summary

The **Scientific Knowledge Integration & Evidence Graph Engine** introduces long-term scientific memory to Project GOAT. Rather than treating every validated hypothesis or research finding independently, this engine constructs an evolving, deterministic scientific knowledge graph (`ScientificKnowledgeGraph`) that accumulates evidence across months or years of automated quantitative research.

Key design guarantees:
- **Absolute Determinism**: Zero machine learning, zero LLM reasoning, zero probabilistic inference.
- **Immutable Domain Models**: All core models (`KnowledgeNode`, `KnowledgeEdge`, `IntegratedKnowledge`, `ConflictRecord`, `EvidenceMergeRecord`, `KnowledgeStateVersion`) are strictly frozen Pydantic models.
- **Stable Identifiers & Canonical Hashes**: All identifiers (`KND_<HEX16>`, `KED_<HEX16>`, `IKN_<HEX16>`, `CFL_<HEX16>`, `EMG_<HEX16>`, `KVR_<HEX16>`) are derived deterministically using canonical SHA-256 digests.
- **Complete Provenance & Replayability**: Every state update is version-tracked (`KnowledgeEvolutionEngine`), allowing complete deterministic replay of past knowledge graph states.
- **SQLite Persistence**: Full round-trip persistence with referential integrity (`PRAGMA foreign_keys = ON`).

---

## 2. Scientific Knowledge Graph

The `ScientificKnowledgeGraph` maintains an in-memory deterministic directed graph of scientific domain entities.

### Node Types (`KnowledgeNodeType`)
- `HYPOTHESIS`: Formulated research hypothesis.
- `VALIDATION`: Completed statistical validation run.
- `EXPERIMENT`: Empirical experiment execution.
- `EVIDENCE`: Raw or synthesized evidence artifact.
- `THEORY`: Higher-order scientific theory or model.
- `FINDING`: Empirical finding or anomaly observation.
- `FEATURE`: Predictive feature or quantitative signal.
- `STUDY`: Research study container.
- `PROGRAM`: Research program container.

### Graph Operations
- `add_node(node)` / `add_edge(edge)` / `remove_edge(edge_id)`
- `lookup_node(node_id)` / `lookup_edge(edge_id)` / `lookup_evidence(target_id)`
- `lookup_relationships(node_id, direction)`
- `neighborhood_queries(node_id, depth)`
- `traversal(start_node_id, max_depth, mode)` (Deterministic BFS / DFS)
- `to_dict()` / `from_dict()` / `serialize()` / `deserialize()`
- `replay_events(events)`

---

## 3. Conflict Detection Engine

The `ConflictDetector` evaluates pairwise scientific findings using deterministic, rule-based logic to detect agreement, contradictions, and version supersessions.

### Conflict Classifications (`ConflictType`)
- `SUPPORTED`: Validations confirm findings with aligned confidence.
- `PARTIALLY_SUPPORTED`: Both validate findings with confidence discrepancy or partial parameter overlap.
- `CONTRADICTED`: Opposite validation decisions (PASSED vs FAILED) for identical hypothesis/feature.
- `DUPLICATED`: Identical findings, parameters, and confidence.
- `SUPERSEDED`: Newer or higher-version validation overrides an earlier validation.
- `INSUFFICIENT_EVIDENCE`: Confidence or sample size below validation threshold.

### Severities (`ConflictSeverity`)
- `NONE`, `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`

---

## 4. Evidence Integration Engine

The `EvidenceMerger` accumulates multi-source research findings into an aggregate `EvidenceMergeRecord` (`EMG_<HEX16>`).

### Accumulation Formulas
- **Confidence Accumulation**: Independent noisy-OR formula: $1 - \prod (1 - c_i)$ bounded to $[0.0, 1.0]$.
- **Reproducibility Accumulation**: Arithmetic mean of component reproducibility scores.
- **Consensus Accumulation**: Ratio of supporting evidence to total evidence count.
- **References Accumulated**:
  - Experiment References (`experiment_refs`)
  - Study References (`study_refs`)
  - Execution References (`execution_refs`)
  - Feature References (`feature_refs`)

---

## 5. Knowledge Evolution & Versioning

The `KnowledgeEvolutionEngine` tracks every integration event as an immutable `KnowledgeStateVersion` (`KVR_<HEX16>`).

- Sequential, 1-indexed version numbering.
- Parent version tracking (`parent_version_id`).
- Immutable snapshot of both `IntegratedKnowledge` and `ScientificKnowledgeGraph` states.
- Replay support: `replay_version(version_id)` reconstructs exact historical states.

---

## 6. Persistence Architecture

All data structures are persisted to SQLite via dedicated repository classes:

- `KnowledgeRepository`: Table `knowledge_nodes`
- `GraphRepository`: Table `knowledge_edges`
- `ConflictRepository`: Table `conflict_records`
- `IntegrationRepository`: Tables `integrated_knowledge` and `knowledge_versions`
- `EvidenceRepository`: Table `evidence_merge_records`
- `ReportRepository`: Table `integration_reports`

All tables enforce foreign-key integrity constraints and round-trip fidelity.

---

## 7. Reporting & Canonical Exports

Subpackage `goat.integration.reporting` provides markdown rendering and canonical JSON export for:
- `KnowledgeIntegrationReport`
- `ConflictReport`
- `KnowledgeGraphReport`
- `EvidenceMergeReport`
- `KnowledgeEvolutionReport`

---

## 8. Public API

Exposed through `goat.integration.__all__`:

```python
from goat.integration import (
    ScientificKnowledgeIntegrationEngine,
    ScientificKnowledgeGraph,
    ConflictDetector,
    EvidenceMerger,
    KnowledgeNode,
    KnowledgeEdge,
    IntegratedKnowledge,
    ConflictRecord,
    EvidenceMergeRecord,
    KnowledgeStateVersion,
    KnowledgeRepository,
    GraphRepository,
    ConflictRepository,
    IntegrationRepository,
    EvidenceRepository,
    ReportRepository,
    KnowledgeIntegrationReport,
    ConflictReport,
    KnowledgeGraphReport,
    EvidenceMergeReport,
    KnowledgeEvolutionReport,
)
```

---

## 9. Code Example

```python
import sqlite3
from goat.integration import ScientificKnowledgeIntegrationEngine

# 1. Initialize Engine with SQLite connection
conn = sqlite3.connect(":memory:")
engine = ScientificKnowledgeIntegrationEngine(conn=conn)

# 2. Process validation run
val_payload = {
    "validation_id": "VAL_2026_001",
    "hypothesis_id": "HYP_MOM_01",
    "experiment_id": "EXP_MOM_01",
    "title": "Momentum Signal Validation",
    "confidence": 0.85,
    "reproducibility": 0.90,
    "status": "PASSED",
    "feature_refs": ["momentum_10d"],
}

ik, report = engine.process_validation_run(
    validation_payload=val_payload,
    timestamp="2026-07-30T12:00:00Z",
)

print(report.to_markdown())
```

---

## 10. Future Extension Points

- **Multi-tenant Knowledge Graph Isolation**: Support workspace-isolated subgraphs with cross-graph bridge edges.
- **Sub-graph Isomorphism Searching**: Deterministic subgraph motif matching for identifying recurring validation topologies.
- **Automated Re-validation Triggers**: Automatic scheduling of re-validation tasks when conflicts reach `CRITICAL` severity.
