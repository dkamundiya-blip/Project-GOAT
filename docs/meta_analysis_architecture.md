# Project GOAT — Scientific Meta-Analysis & Research Intelligence Architecture

Version: v0.7 — Step 5.9  
Status: Active Implementation / Certified  
Package: `goat.meta_analysis`  

---

## 1. Architecture Summary

The **Scientific Meta-Analysis & Research Intelligence Engine** implements higher-order deterministic intelligence for Project GOAT. Rather than treating validated hypotheses as isolated knowledge graph entities, this engine performs systematic meta-analysis across accumulated scientific memory to discover recurring evidence, persistent scientific themes, reproducible research clusters, recurring patterns, and research trends.

Design Principles:
- **Zero AI / ML Reasoning**: Strictly rule-based, deterministic, and mathematical calculations. No LLMs, neural networks, or probabilistic classifiers.
- **Immutable Pydantic Domain Models**: `ResearchCluster`, `ResearchPattern`, `ResearchTrend`, `ScientificSummary`, `ResearchIntelligenceMetrics`, and `MetaAnalysisResult` are strictly frozen Pydantic models.
- **Deterministic Identifiers**: Stable prefix IDs (`RCL_<HEX16>`, `RPT_<HEX16>`, `RTD_<HEX16>`, `SCS_<HEX16>`, `RIM_<HEX16>`, `MAR_<HEX16>`) generated via SHA-256 digests.
- **Full Replay & Auditability**: Complete deterministic state replay via `analysis_repo.get_result(analysis_id)` and version-based re-execution.
- **SQLite Persistence**: Dedicated repositories enforcing schema integrity and foreign-key constraints.

---

## 2. Cluster Engine

`ClusterEngine` provides deterministic rule-based (non-ML) clustering:
- `THEME`: Grouping by feature or theme tags in metadata.
- `VALIDATION`: Grouping by validation status (`PASSED`, `FAILED`, `SUPPORTED`).
- `EVIDENCE`: Grouping by shared evidence artifact references.
- `EXPERIMENT`: Grouping by experiment ID / setup.
- `STUDY`: Grouping by study ID.
- `KNOWLEDGE`: Grouping by topological graph connectivity in `ScientificKnowledgeGraph`.

---

## 3. Pattern Discovery Engine

`PatternDiscoveryEngine` evaluates research data to discover:
- `RECURRING_EVIDENCE`: Evidence artifacts referenced across multiple validation runs.
- `RECURRING_RELATIONSHIP`: Repeated topological edge patterns.
- `FREQUENTLY_VALIDATED`: Hypotheses or features passing validation repeatedly.
- `LONG_TERM_REPRODUCIBILITY`: Research clusters with high reproducibility maintained over time.
- `STABLE_OBSERVATION`: Features showing zero contradiction records.
- `SCIENTIFIC_ANOMALY`: High confidence findings with elevated contradiction rates.
- `WEAK_EVIDENCE_REGION`: Low confidence (< 0.50) or sparse evidence clusters.
- `EMERGING_DOMAIN`: Newly established clusters with expanding validation activity.

---

## 4. Trend Analysis Engine

`TrendAnalysisEngine` classifies research dynamics into:
- `GROWING`: Increasing validation volume & confidence over time.
- `DECLINING`: Decreasing confidence or failing validation outcomes.
- `STABLE`: High confidence & reproducibility maintained consistently.
- `CONFLICTING`: Elevated contradiction frequency across validation runs.
- `UNRESOLVED`: Insufficient evidence or equal pass/fail split.
- `DORMANT`: Inactive topics with no recent validation activity.

---

## 5. Research Intelligence Metrics

`ResearchIntelligenceEngine` calculates quantitative metrics:
- **Knowledge Density**: Ratio of validated nodes to total graph nodes.
- **Evidence Density**: Ratio of evidence artifacts to graph topology size.
- **Validation Stability**: Ratio of passed validation runs to total runs.
- **Consensus Stability**: Average consensus rating across integrated knowledge states.
- **Research Breadth**: Total unique research topics / feature domains covered.
- **Research Depth**: Structural path depth in knowledge graph traversals.
- **Knowledge Maturity**: $0.4 \times \text{Validation Stability} + 0.3 \times \text{Consensus Stability} + 0.3 \times \text{Knowledge Density}$.
- **Scientific Confidence**: $0.5 \times \text{Validation Stability} + 0.5 \times \text{Evidence Density}$.

---

## 6. Scientific Summary Engine

`ScientificSummaryEngine` generates executive scientific summaries containing:
- Counts of validated knowledge, integrated knowledge, conflicts, clusters, patterns, and trends.
- Identified strongest and weakest research areas.
- Active unresolved contradictions.
- Deterministic recommendations for future research investigation.

---

## 7. Persistence & Replay

Repositories:
- `ClusterRepository`: Table `research_clusters`
- `PatternRepository`: Table `research_patterns`
- `TrendRepository`: Table `research_trends`
- `SummaryRepository`: Table `scientific_summaries`
- `MetaAnalysisRepository`: Table `meta_analysis_results`
- `ReportRepository`: Table `meta_analysis_reports`

Replay is executed via `engine.replay_analysis(analysis_id)`, loading exact historical meta-analysis results from persistence.

---

## 8. Public API

Exposed through `goat.meta_analysis.__all__`:

```python
from goat.meta_analysis import (
    ScientificMetaAnalysisEngine,
    ClusterEngine,
    PatternDiscoveryEngine,
    TrendAnalysisEngine,
    ResearchIntelligenceEngine,
    ScientificSummaryEngine,
    ResearchCluster,
    ResearchPattern,
    ResearchTrend,
    ScientificSummary,
    ResearchIntelligenceMetrics,
    MetaAnalysisResult,
    MetaAnalysisReport,
    ClusterRepository,
    PatternRepository,
    TrendRepository,
    SummaryRepository,
    MetaAnalysisRepository,
    ReportRepository,
)
```

---

## 9. Example Usage

```python
import sqlite3
from goat.meta_analysis import ScientificMetaAnalysisEngine

conn = sqlite3.connect(":memory:")
engine = ScientificMetaAnalysisEngine(conn=conn)

validations = [
    {"validation_id": "VAL_001", "hypothesis_id": "HYP_MOM", "status": "PASSED", "confidence": 0.85},
    {"validation_id": "VAL_002", "hypothesis_id": "HYP_MOM", "status": "PASSED", "confidence": 0.88},
]

result, report = engine.run_meta_analysis(
    integrated_knowledge_list=[],
    graph=None,
    validations=validations,
    conflicts=[],
    timestamp="2026-07-30T12:00:00Z",
)

print(report.to_markdown())
```

---

## 10. Future Extension Points

- **Cross-Domain Meta-Synthesizers**: Cross-referencing meta-analysis trends across different asset classes or market regimes.
- **Automated Research Portfolio Balancing**: Using Knowledge Maturity and Research Breadth metrics to adjust prioritization weights for automated research campaign planning.
