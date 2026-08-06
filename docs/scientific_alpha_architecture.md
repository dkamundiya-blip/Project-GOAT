# Project GOAT — Scientific Alpha & Quantitative Edge Architecture

Version: v0.7 — Step 6.0 (Phase VI)  
Status: Active Implementation / Certified  
Package: `goat.alpha`  

---

## 1. Architecture Summary

Phase VI introduces the **Scientific Alpha Engine**, shifting Project GOAT's objective from accumulating scientific knowledge to discovering, measuring, ranking, and continuously evaluating candidate quantitative market edges (`ScientificEdge`).

Key Design Guarantees:
- **No Signal Generation / No Black-Box Trading**: The engine evaluates candidate edges based on empirical scientific evidence and quality metrics. It does NOT generate trading signals.
- **Zero AI / ML Reasoning**: No neural networks, no probabilistic ML classifiers, no LLM reasoning. All calculations, scoring, and rankings are 100% deterministic, rule-based, and auditable.
- **Immutable Pydantic Models**: Core domain models (`ScientificEdge`, `EdgeEvidence`, `EdgeScore`, `EdgeRanking`, `EdgeExplainabilityRecord`) are strictly frozen Pydantic models.
- **Deterministic Identifiers**: Prefix IDs (`SED_<HEX16>`, `EEV_<HEX16>`, `ESC_<HEX16>`, `ERK_<HEX16>`, `EEX_<HEX16>`, `SAR_<HEX16>`) derived using canonical SHA-256 digests.
- **Complete Explainability & Traceability**: Every discovered edge includes complete origin tracking, evidence references, and narrative scientific explanations.
- **SQLite Persistence & Replay**: Round-trip persistence with referential integrity (`PRAGMA foreign_keys = ON`) and exact state replay.

---

## 2. Edge Discovery Pipeline

`EdgeDiscoveryEngine` evaluates research artifacts across:
1. Validated hypotheses
2. Integrated knowledge states
3. Research clusters (`ResearchCluster`)
4. Recurring patterns (`ResearchPattern`)
5. Stable trends (`ResearchTrend`)
6. Meta-analysis results

### Edge Maturity Stages (`EdgeMaturity`)
- `NEW`: Single passed validation run.
- `EXPERIMENTAL`: Multiple validations within a single experiment.
- `EMERGING`: Supported by a ResearchCluster or Recurring Pattern.
- `VALIDATED`: Supported by IntegratedKnowledge with consensus > 0.70.
- `MATURE`: Supported by a GROWING or STABLE trend with reproducibility > 0.85.
- `FOUNDATIONAL`: Supported across multiple integrated knowledge states with zero unhandled contradictions.

---

## 3. Scientific Scoring Framework

`EdgeScoringEngine` computes multi-dimensional quality scores:
- **Evidence Strength**: Based on supporting evidence volume and confidence ratings.
- **Scientific Confidence**: Overall confidence rating derived from component validations.
- **Reproducibility**: Empirical reproducibility score across independent experiments.
- **Stability**: Performance and effect stability.
- **Robustness**: Parameter stability and structural robustness.
- **Longevity**: Maturity stage weighting ($0.20$ to $1.00$).
- **Conflict Penalty**: Deducted penalty based on unhandled contradiction records.
- **Overall Edge Score**:
  $$\text{Overall Score} = \max\left(0.0, \frac{\text{Quality} + \text{Evidence Strength} + \text{Reproducibility} + \text{Stability} + \text{Longevity}}{5} - \text{Conflict Penalty}\right)$$

---

## 4. Ranking Engine & Stable Tie-Breaking

`EdgeRankingEngine` ranks candidate edges deterministically:
- Primary sort key: `overall_edge_score` (descending).
- Tie-breaker 1: `scientific_quality` (descending).
- Tie-breaker 2: `reproducibility_score` (descending).
- Tie-breaker 3: `edge_id` (alphabetically ascending).

This guarantees 100% stable, deterministic rankings across arbitrary execution runs.

---

## 5. Edge Explainability Architecture

`EdgeEvidenceAggregator` constructs `EdgeExplainabilityRecord` objects for complete scientific traceability:
- Origin reference (`originating_hypotheses`)
- Supporting evidence IDs
- Supporting validation runs
- Supporting experiments
- Supporting studies
- Supporting clusters and trends
- Narrative scientific explanation string

---

## 6. Persistence & Replay

Repositories:
- `ScientificEdgeRepository`: Table `scientific_edges`
- `EdgeEvidenceRepository`: Tables `edge_evidence` & `edge_explainability_records`
- `EdgeScoreRepository`: Table `edge_scores`
- `EdgeRankingRepository`: Table `edge_rankings`
- `EdgeReportRepository`: Table `alpha_reports`

Replay support: `engine.replay_ranking(ranking_id)` reconstructs exact historical `EdgeRanking` objects from SQLite persistence.

---

## 7. Public API

Exposed through `goat.alpha.__all__`:

```python
from goat.alpha import (
    ScientificAlphaDiscoveryEngine,
    EdgeDiscoveryEngine,
    EdgeScoringEngine,
    EdgeEvidenceAggregator,
    EdgeRankingEngine,
    ScientificEdge,
    EdgeEvidence,
    EdgeScore,
    EdgeRanking,
    EdgeExplainabilityRecord,
    ScientificEdgeRepository,
    EdgeEvidenceRepository,
    EdgeScoreRepository,
    EdgeRankingRepository,
    EdgeReportRepository,
)
```

---

## 8. Code Example

```python
import sqlite3
from goat.alpha import ScientificAlphaDiscoveryEngine

conn = sqlite3.connect(":memory:")
engine = ScientificAlphaDiscoveryEngine(conn=conn)

validations = [
    {"validation_id": "VAL_001", "hypothesis_id": "HYP_MOM_10D", "status": "PASSED", "confidence": 0.88, "reproducibility": 0.90},
    {"validation_id": "VAL_002", "hypothesis_id": "HYP_MOM_10D", "status": "PASSED", "confidence": 0.92, "reproducibility": 0.94},
]

ranking, report = engine.execute_alpha_discovery(
    validations=validations,
    integrated_knowledge_list=[],
    meta_result=None,
    conflicts=[],
    timestamp="2026-07-30T12:00:00Z",
)

print(report.to_markdown())
```

---

## 9. Future Extension Points

- **Multi-Factor Alpha Combinators**: Combining independent candidate edges into composite multi-factor edge models.
- **Dynamic Decay Modeling**: Tracking time-decay of edge stability as market regimes shift over multi-year evaluation windows.
