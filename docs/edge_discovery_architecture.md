# Quantitative Edge Discovery Engine Architecture

## System Overview

Project GOAT Version 0.9 — Step 9.9 introduces the **Quantitative Edge Discovery Engine** (`goat/edge_discovery/`).

This subsystem is the first subsystem in Project GOAT authorized to discover candidate quantitative edges and repeatable statistical behaviors from completed experiments, evidence records, market microstructure observations, and controlled live validation history.

### Non-Negotiable Research Protocol
1. **NO Trading Signals**: Does not produce buy/sell signals.
2. **NO Order Execution**: Does not interact with brokers or execute trades.
3. **NO Parameter Optimization**: Does not optimize parameters or fit curves.
4. **NO Technical Analysis / Indicators**: NO RSI, MACD, ICT, SMC, Wyckoff, Fibonacci, or chart patterns.
5. **Candidates Only**: Discovers candidate quantitative edges; final edge approval belongs exclusively to Governance.

---

## Package Structure & Subsystem Inventory

```
goat/edge_discovery/
├── __init__.py                # Public API exports
├── engine.py                  # Master Quantitative Edge Discovery Engine
├── core/
│   ├── enums.py               # EdgeCategory, PatternType, ValidationStatus, etc.
│   ├── canonical.py           # Canonical JSON & SHA-256 ID generators
│   ├── models.py              # Immutable Pydantic V2 domain models
│   └── __init__.py
├── mining/
│   ├── engine.py              # PatternMiningEngine
│   └── __init__.py
├── clustering/
│   ├── engine.py              # PatternClusteringEngine
│   └── __init__.py
├── novelty/
│   ├── engine.py              # NoveltyAssessmentEngine
│   └── __init__.py
├── scoring/
│   ├── engine.py              # EdgeScoringEngine
│   └── __init__.py
├── validation/
│   ├── engine.py              # DiscoveryValidationEngine
│   └── __init__.py
├── reporting/
│   ├── reports.py             # EdgeDiscoveryReportGenerator
│   └── __init__.py
└── persistence/
    ├── sqlite.py              # SQLite repositories & PersistenceContext
    └── __init__.py
```

---

## Domain Models & Canonical ID Mapping

All models are immutable Pydantic V2 models (`ConfigDict(frozen=True, extra="forbid")`).

| Model Name | ID Prefix | Canonical Hash Fields |
|---|---|---|
| `EdgeCandidate` | `EDC_` | name, category, pattern_ids, symbol, version |
| `EdgePattern` | `EPT_` | pattern_type, symbol, sample_size, statistical_significance, version |
| `PatternCluster` | `CLS_` | cluster_name, pattern_ids, version |
| `NoveltyAssessment` | `NOV_` | candidate_id, max_similarity_score, status, version |
| `EdgeScore` | `SCR_` | candidate_id, overall_score, tier, version |
| `DiscoveryDecision` | `DSC_` | candidate_id, status, reason, timestamp, version |
| `DiscoverySummary` | `DSM_` | timestamp, total_candidates, total_validated, version |

---

## Sub-Engines & Responsibilities

1. **PatternMiningEngine**: Mines recurring statistical behaviors across microstructure observations and evidence without using technical indicators or chart patterns.
2. **PatternClusteringEngine**: Groups highly similar discovered patterns to reduce duplicate discoveries.
3. **NoveltyAssessmentEngine**: Evaluates whether a candidate edge is genuinely novel compared to archived edges.
4. **EdgeScoringEngine**: Computes multi-dimensional institutional quality scores (0..100) using support, stability, consistency, cross-regime robustness, sample size, variance, confidence, and live validation compatibility without parameter optimization.
5. **DiscoveryValidationEngine**: Enforces research protocol rules and fails closed upon detecting insufficient observations, duplicate edges, poor confidence, overfit evidence, or single-regime behavior.
6. **MasterEdgeDiscoveryEngine**: Master orchestrator integrating all sub-engines, database persistence, and reporting.

---

## Persistence & Reporting Architecture

- **SQLite WAL Repositories**:
  - `PatternRepository`
  - `ClusterRepository`
  - `EdgeRepository`
  - `NoveltyRepository`
  - `ScoreRepository`
  - `DecisionRepository`
  - `SummaryRepository`
  - `EdgeDiscoveryPersistenceContext`
- **Report Generator**:
  - `EdgeDiscoveryReportGenerator`: Markdown & Canonical JSON export for Executive Reports, Candidate Reports, Novelty Reports, Scoring Reports, and Summary Reports.
