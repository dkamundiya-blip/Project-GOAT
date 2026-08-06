# Project GOAT — Composite Edge Synthesis Architecture

Version: v0.7 — Step 6.2 (Phase VI)  
Status: Active Implementation / Certified  
Package: `goat.composite`  

---

## 1. Architecture Summary

Step 6.2 introduces the **Composite Edge Synthesis & Portfolio Intelligence Engine** (`goat.composite`). Robust decision-making in quantitative systems emerges from combining multiple independent market edges that reinforce one another while minimizing conflicting evidence. This engine discovers, evaluates, and ranks combinations of scientifically validated edges (`ScientificEdge`) without producing trading signals or relying on non-deterministic AI/ML optimization.

Key Design Guarantees:
- **No Signal Generation / No Black-Box Portfolio Construction**: Evaluates composite edge combinations based on scientific reinforcement and synergy metrics. Does NOT generate trading signals.
- **Zero AI / ML Reasoning**: Rule-based deterministic synthesis and conflict resolution. All calculations are 100% reproducible and auditable.
- **Immutable Pydantic Models**: Core domain models (`CompositeEdge`, `CompositeEvidence`, `CompositeScore`, `CompositeRanking`, `CompositeExplainabilityRecord`) are strictly frozen Pydantic models.
- **Deterministic Identifiers**: Prefix IDs (`CMP_<HEX16>`, `CEV_<HEX16>`, `CSC_<HEX16>`, `CRK_<HEX16>`, `CEX_<HEX16>`, `CAR_<HEX16>`) derived via canonical SHA-256 digests.
- **Complete Explainability & Traceability**: Every composite edge includes complete origin tracking, evidence references, compatibility rationale, conflict analysis, and narrative scientific explanations.
- **SQLite Persistence & Replay**: Full round-trip persistence with referential integrity (`PRAGMA foreign_keys = ON`) and exact state replay.

---

## 2. Synthesis Pipeline

`CompositeEdgeSynthesisEngine` evaluates combinations of active `ScientificEdge` objects:
- Pairwise combination discovery
- Multi-edge tuple evaluation
- Incompatible combination rejection via `CompositeConflictEngine`

---

## 3. Conflict Analysis Framework

`CompositeConflictEngine` evaluates potential conflict points:
1. **Direct Contradiction**: Opposing hypothesis directions (e.g. Momentum vs Reversal).
2. **Duplicate Evidence**: Over-reliance on identical validation runs.
3. **Weak Reinforcement**: Sub-threshold mutual confidence.
4. **Redundant Knowledge**: Structurally identical edge pairs.
5. **Mutually Exclusive Applicability**: Incompatible active market regimes.

Conflict severity stages: `NONE`, `LOW`, `MEDIUM`, `HIGH`, `CRITICAL_REJECTION`.

---

## 4. Synergy & Quality Scoring Framework

`CompositeScoringEngine` computes multi-dimensional quality metrics:
- **Synergy Score**: Knowledge reinforcement from independent edge confirmation.
- **Robustness Score**: Mean structural robustness across component edges.
- **Stability Score**: Mean historical stability across component edges.
- **Diversity Score**: Hypothesis and evidence diversity.
- **Conflict Penalty**: Deducted penalty based on conflict severity.
- **Explainability Score**: Scientific explanation completeness.
- **Reproducibility Score**: Mean empirical reproducibility.
- **Overall Score**: Aggregate quality metric bounded to $[0.0, 1.0]$.

---

## 5. Ranking Engine & Stable Tie-Breaking

`CompositeRankingEngine` ranks `CompositeEdge` objects deterministically:
- Primary sort key: `overall_score` (descending).
- Tie-breaker 1: `synergy_score` (descending).
- Tie-breaker 2: `robustness_score` (descending).
- Tie-breaker 3: `composite_id` (alphabetically ascending).

---

## 6. Explainability Architecture

`CompositeEdgeSynthesisEngine` constructs `CompositeExplainabilityRecord` objects providing 100% scientific traceability:
- Participating edge IDs
- Originating hypotheses and validation runs
- Supporting evidence IDs
- Primary scientific explanation
- Compatibility explanation
- Conflict evaluation rationale

---

## 7. Persistence & Replay

Repositories:
- `CompositeRepository`: Table `composite_edges`
- `CompositeEvidenceRepository`: Tables `composite_evidence` & `composite_explainability_records`
- `CompositeScoreRepository`: Table `composite_scores`
- `CompositeRankingRepository`: Table `composite_rankings`
- `CompositeReportRepository`: Table `composite_reports`

Replay support: `coordinator.replay_ranking(ranking_id)` and `coordinator.replay_composite(composite_id)` restore exact historical models from SQLite persistence.

---

## 8. Public API

Exposed through `goat.composite.__all__`:

```python
from goat.composite import (
    CompositeEdgeEngineCoordinator,
    CompositeEdgeSynthesisEngine,
    CompositeConflictEngine,
    CompositeScoringEngine,
    CompositeRankingEngine,
    CompositeEdge,
    CompositeEvidence,
    CompositeScore,
    CompositeRanking,
    CompositeExplainabilityRecord,
    CompositeRepository,
    CompositeEvidenceRepository,
    CompositeScoreRepository,
    CompositeRankingRepository,
    CompositeReportRepository,
)
```

---

## 9. Code Example

```python
import sqlite3
from goat.composite import CompositeEdgeEngineCoordinator
from goat.alpha import ScientificEdge

conn = sqlite3.connect(":memory:")
coordinator = CompositeEdgeEngineCoordinator(conn=conn)

edge1 = ScientificEdge(
    edge_id="SED_1111111111111111",
    title="Quantitative Edge: MOM_10D",
    confidence=0.88,
    reproducibility=0.90,
    discovery_timestamp="2026-07-30T12:00:00Z",
)

edge2 = ScientificEdge(
    edge_id="SED_2222222222222222",
    title="Quantitative Edge: VOL_BREAKOUT",
    confidence=0.85,
    reproducibility=0.86,
    discovery_timestamp="2026-07-30T12:00:00Z",
)

ranking, report = coordinator.execute_composite_synthesis_workflow(
    active_edges=[edge1, edge2],
    timestamp="2026-07-30T12:00:00Z",
)

print(report.to_markdown())
```

---

## 10. Future Extension Points

- **Hierarchical Multi-Layer Composites**: Synthesizing higher-order composite edges from existing lower-order composites.
- **Cross-Regime Portfolio Matrices**: Mapping composite edge performance profiles across dynamic multi-regime transition matrices.
