# Project GOAT v0.9 — Edge Knowledge Graph & Scientific Relationship Engine Architecture

## Subsystem Overview
The **Edge Knowledge Graph & Scientific Relationship Engine** (`goat/knowledge/`) is the institutional scientific memory subsystem of Project GOAT Version 0.9. Its sole responsibility is building, maintaining, traversing, validating, and persisting an unbroken scientific relationship graph linking all research artifacts in GOAT.

It DOES NOT discover edges, DOES NOT evaluate statistics, DOES NOT execute trades, DOES NOT make governance decisions, and DOES NOT analyze markets. It ONLY records and audits scientific relationships.

---

## Unbroken Scientific Lineage Chain
Every promoted edge must be traceable through an unbroken scientific chain:

```
[HYPOTHESIS] 
     ↓ (GENERATES_EVIDENCE)
[EVIDENCE]
     ↓ (CONDUCTS_EXPERIMENT)
[EXPERIMENT]
     ↓ (EVALUATES_STATISTICS)
[STATISTICAL_EVALUATION]
     ↓ (VALIDATES_LIVE)
[LIVE_VALIDATION]
     ↓ (DECIDES_GOVERNANCE)
[GOVERNANCE_DECISION]
     ↓ (DISCOVERS_EDGE)
[DISCOVERED_EDGE]
     ↓ (ARCHIVES_ARTIFACT)
[ARCHIVE]
```

---

## Canonical ID Prefix Taxonomy

All entity IDs are SHA-256 uppercase hex digests with canonical prefix mapping:

| Entity / Model | ID Prefix | Canonical Function |
|---|---|---|
| `KnowledgeNode` | `KND_` | `compute_knowledge_node_id(...)` |
| `KnowledgeRelationship` | `REL_` | `compute_knowledge_relationship_id(...)` |
| `KnowledgeGraph` | `KGR_` | `compute_knowledge_graph_id(...)` |
| `ScientificPath` | `PTH_` | `compute_scientific_path_id(...)` |
| `RelationshipValidation` | `VAL_` | `compute_relationship_validation_id(...)` |
| `KnowledgeSummary` | `KSM_` | `compute_knowledge_summary_id(...)` |

---

## Sub-Engine Responsibilities

1. **`KnowledgeGraphEngine`** (`graph/engine.py`): Creates `KnowledgeNode` instances for all GOAT scientific entities and assembles container `KnowledgeGraph` objects.
2. **`RelationshipEngine`** (`relationships/engine.py`): Creates directed `KnowledgeRelationship` links establishing scientific lineage.
3. **`TraversalEngine`** (`traversal/engine.py`): Executes deterministic path-finding DFS, ancestor extraction, descendant extraction, and lineage tracing returning `ScientificPath`.
4. **`ValidationEngine`** (`validation/engine.py`): Audits knowledge graphs for broken chains, missing evidence, orphan nodes, circular cycles, and duplicate relationships.
5. **`MasterKnowledgeEngine`** (`engine.py`): Unified master orchestrator integrating graph creation, relationships, traversal, validation, SQLite persistence, and reporting.

---

## SQLite Persistence Architecture

SQLite WAL (`PRAGMA journal_mode = WAL;`) and Foreign Key enforcement (`PRAGMA foreign_keys = ON;`).
Repositories:
- `KnowledgeNodeRepository` (`knowledge_graph_nodes`)
- `RelationshipRepository` (`knowledge_graph_relationships`)
- `GraphRepository` (`knowledge_graphs`)
- `TraversalRepository` (`scientific_paths`)
- `ValidationRepository` (`relationship_validations`)
- `SummaryRepository` (`knowledge_summaries`)
- `KnowledgePersistenceContext`
