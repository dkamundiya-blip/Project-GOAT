# Project GOAT v0.9 — Institutional Research Intelligence & Meta-Analysis Engine Architecture

## Subsystem Overview
The **Institutional Research Intelligence & Meta-Analysis Engine** (`goat/intelligence/`) is the institutional self-analytic subsystem of Project GOAT Version 0.9. Its sole responsibility is performing scientific analysis on Project GOAT's own accumulated research history.

It DOES NOT analyze market prices directly, DOES NOT generate trading signals, DOES NOT execute trades, DOES NOT make portfolio or risk sizing allocations, DOES NOT promote edges, and DOES NOT make governance decisions. It ONLY analyzes research history to answer institutional meta-scientific questions and suggest future scientific research priorities.

---

## Institutional Questions Answered
1. **Hypothesis Category Success Rates**: Which categories of hypotheses succeed most often?
2. **Experiment Design Efficiency**: Which experiment designs produce the strongest evidence with minimal sample waste?
3. **Regime Invalidation Impact**: Which market regimes consistently invalidate discoveries?
4. **Evidence Predictive Strength**: Which evidence types have the highest predictive value?
5. **Research Time Waste Reduction**: Which research paths waste the most time?
6. **Edge Longevity**: Which edge families survive longest?

---

## Canonical ID Prefix Taxonomy

All entity IDs are SHA-256 uppercase hex digests with canonical prefix mapping:

| Entity / Model | ID Prefix | Canonical Function |
|---|---|---|
| `ResearchInsight` | `RIN_` | `compute_research_insight_id(...)` |
| `MetaAnalysis` | `MTA_` | `compute_meta_analysis_id(...)` |
| `ResearchTrend` | `TRD_` | `compute_research_trend_id(...)` |
| `InstitutionalRecommendation` | `REC_` | `compute_institutional_recommendation_id(...)` |
| `ResearchHealth` | `RHL_` | `compute_research_health_id(...)` |
| `IntelligenceSummary` | `ISM_` | `compute_intelligence_summary_id(...)` |

---

## Sub-Engine Responsibilities

1. **`ResearchAnalyticsEngine`** (`analytics/engine.py`): Aggregates historical research outcomes (hypothesis success rates, experiment efficiency, regime invalidation counts, research time waste).
2. **`MetaAnalysisEngine`** (`meta/engine.py`): Computes higher-order meta-analysis patterns, pooled effect sizes, heterogeneity $I^2$, and edge family survival rates.
3. **`InsightEngine`** (`insights/engine.py`): Produces explainable institutional research insights (`ResearchInsight`).
4. **`RecommendationEngine`** (`recommendations/engine.py`): Formulates actionable scientific research recommendations (`InstitutionalRecommendation`) solely concerning future scientific research priorities.
5. **`MasterIntelligenceEngine`** (`engine.py`): Unified master orchestrator integrating analytics, meta-analyses, insights, recommendations, research health scoring, SQLite persistence, and reporting.

---

## SQLite Persistence Architecture

SQLite WAL (`PRAGMA journal_mode = WAL;`) and Foreign Key enforcement (`PRAGMA foreign_keys = ON;`).
Repositories:
- `InsightRepository` (`research_insights`)
- `MetaAnalysisRepository` (`meta_analyses`)
- `TrendRepository` (`research_trends`)
- `RecommendationRepository` (`institutional_recommendations`)
- `HealthRepository` (`research_health`)
- `SummaryRepository` (`intelligence_summaries`)
- `IntelligencePersistenceContext`
