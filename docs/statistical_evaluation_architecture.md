# STATISTICAL EVALUATION ENGINE ARCHITECTURE
## PROJECT GOAT VERSION 0.9 — STEP 9.4 SPECIFICATION

**Document Version**: 1.0.0  
**Authorizing Body**: Institutional Quantitative Research Board  
**Executive Authority**: Chief Scientific Officer & Head of Quantitative Research  
**Target Subsystem**: `goat.statistics`  
**Effective Date**: 2026-08-04  
**Status**: CERTIFIED & FROZEN  

---

## 1. ARCHITECTURE SUMMARY

The **Statistical Evaluation Engine** (`goat.statistics`) is the empirical evaluation layer for Project GOAT Version 0.9. It is the **first component allowed to determine whether experimental evidence supports or rejects a scientific hypothesis**.

Crucially, the statistical evaluation subsystem strictly observes append-only principles:
- It **SHALL NEVER** create hypotheses.
- It **SHALL NEVER** collect observations or evidence.
- It **SHALL NEVER** modify existing experiments or manifests.
- It **ONLY** appends immutable statistical evaluation records (`STE_`) and scientific decisions (`EVD_`).
- It **DOES NOT** perform trade sizing or portfolio allocation.

It operates as a pure, objective statistical decision engine governed by SHA-256 canonical digests.

---

## 2. PACKAGE STRUCTURE

```
goat/statistics/
├── __init__.py               # Top-level public API exports with strict __all__
├── engine.py                 # MasterStatisticalEngine facade
├── core/
│   ├── __init__.py           # Core package exports
│   ├── canonical.py          # Deterministic SHA-256 serialization & ID generation
│   ├── enums.py              # EvaluationStatus, ScientificDecision, EvaluationConfidence
│   └── models.py             # Immutable Pydantic V2 domain models
├── evaluation/
│   ├── __init__.py           # Evaluation package exports
│   └── engine.py             # StatisticalEvaluationEngine
├── confidence/
│   ├── __init__.py           # Confidence package exports
│   └── engine.py             # ConfidenceAssessmentEngine
├── significance/
│   ├── __init__.py           # Significance package exports
│   └── engine.py             # SignificanceAssessmentEngine
├── expectancy/
│   ├── __init__.py           # Expectancy package exports
│   └── engine.py             # ExpectancyAssessmentEngine
├── reporting/
│   ├── __init__.py           # Reporting package exports
│   └── reports.py            # Markdown, JSON, Statistical & Summary report generators
└── persistence/
    ├── __init__.py           # Persistence package exports
    └── sqlite.py             # SQLite WAL repositories & context
```

---

## 3. DOMAIN MODEL INVENTORY

All domain models are implemented as immutable Pydantic V2 models with `frozen=True` and `extra="forbid"`:

1. **`StatisticalEvaluation`**:
   - Primary evaluation container entity.
   - Identifier prefix: `STE_<HEX16>`.
   - Fields: `experiment_id`, `hypothesis_id`, `status`, `decision`, `confidence_level`, `confidence_rating`, `p_value`, `effect_size`, `expected_value`, `sample_size`, `evaluator`, `timestamp`, `tags`, `metadata`, `canonical_hash`.

2. **`ConfidenceAssessment`**:
   - Confidence interval calculations and margin of error estimation.
   - Identifier prefix: `CON_<HEX16>`.
   - Fields: `evaluation_id`, `confidence_level`, `lower_bound`, `upper_bound`, `margin_of_error`, `sample_size`, `confidence_rating`, `timestamp`, `metadata`, `canonical_hash`.

3. **`SignificanceAssessment`**:
   - Empirical $p$-value hypothesis testing and multiple-comparison corrections.
   - Identifier prefix: `SIG_<HEX16>`.
   - Fields: `evaluation_id`, `p_value`, `test_statistic`, `alpha_threshold`, `is_significant`, `multiple_comparison_correction`, `adjusted_p_value`, `timestamp`, `metadata`, `canonical_hash`.

4. **`ExpectancyAssessment`**:
   - Mathematical expectation, win/loss ratios, and profit factors.
   - Identifier prefix: `EXP_<HEX16>`.
   - Fields: `evaluation_id`, `expected_value`, `win_rate`, `loss_rate`, `average_gain`, `average_loss`, `profit_factor`, `sample_size`, `timestamp`, `metadata`, `canonical_hash`.

5. **`EvaluationDecision`**:
   - Formal scientific decision regarding hypothesis support/refutation.
   - Identifier prefix: `EVD_<HEX16>`.
   - Fields: `evaluation_id`, `hypothesis_id`, `decision`, `confidence_rating`, `decision_rationale`, `authorizer`, `timestamp`, `metadata`, `canonical_hash`.

6. **`EvaluationSummary`**:
   - Aggregate snapshot of evaluation subsystem counts and decisions.
   - Identifier prefix: `SUM_<HEX16>`.
   - Fields: `total_evaluations`, `total_decisions`, `decision_counts`, `confidence_counts`, `status_counts`, `timestamp`, `metadata`, `canonical_hash`.

---

## 4. CANONICAL ID GENERATION & SHA-256 HASHING

All identifiers are computed deterministically using sorted-key canonical JSON serialization and SHA-256 hashing. Identical inputs yield identical IDs:

- **Evaluation ID**: `STE_<HEX16>` derived from `experiment_id`, `hypothesis_id`, `evaluator`.
- **Confidence ID**: `CON_<HEX16>` derived from `evaluation_id`, `confidence_level`, `margin_of_error`.
- **Significance ID**: `SIG_<HEX16>` derived from `evaluation_id`, `p_value`, `test_statistic`.
- **Expectancy ID**: `EXP_<HEX16>` derived from `evaluation_id`, `expected_value`, `sample_size`.
- **Decision ID**: `EVD_<HEX16>` derived from `evaluation_id`, `decision`, `hypothesis_id`.
- **Summary ID**: `SUM_<HEX16>` derived from `total_evaluations`, `total_decisions`, `timestamp`.

---

## 5. SUB-ENGINE RESPONSIBILITIES

1. **`ConfidenceAssessmentEngine`**:
   - Computes deterministic confidence intervals and margins of error ($z \cdot \sigma / \sqrt{n}$).
   - Classifies confidence level (`VERY_LOW` through `VERY_HIGH`).

2. **`SignificanceAssessmentEngine`**:
   - Evaluates empirical $p$-values and test statistics against $H_0$.
   - Applies Bonferroni and Benjamini-Hochberg false discovery corrections for multiple comparisons.

3. **`ExpectancyAssessmentEngine`**:
   - Calculates mathematical expectancy $\mathbb{E}[X] = (W \cdot \text{Gain}) - (L \cdot \text{Loss})$.
   - Calculates win/loss rates and profit factor without trade sizing.

4. **`StatisticalEvaluationEngine`**:
   - Coordinates evaluations and derives deterministic scientific decisions (`SUPPORTED`, `INCONCLUSIVE`, `REJECTED`, `REQUIRES_MORE_DATA`).
   - Appends immutable decision entities (`EVD_`) without mutating experiments.

---

## 6. SQLITE PERSISTENCE ARCHITECTURE

Persistence is provided by `goat.statistics.persistence.sqlite`:

- **WAL Mode & Foreign Keys**: `PRAGMA foreign_keys = ON; PRAGMA journal_mode = WAL;`
- **Repositories**:
  - `StatisticalRepository`
  - `ConfidenceRepository`
  - `SignificanceRepository`
  - `ExpectancyRepository`
  - `DecisionRepository`
  - `SummaryRepository`
- **Context Manager**: `StatisticalPersistenceContext` managing connection lifecycle and thread safety.

---

## 7. REPORTING GENERATORS

Module `goat.statistics.reporting.reports`:
- `generate_statistical_report(...)`: GFM Markdown report for evaluations.
- `generate_confidence_report(...)`: GFM Markdown report for confidence intervals.
- `generate_significance_report(...)`: GFM Markdown report for hypothesis testing.
- `generate_expectancy_report(...)`: GFM Markdown report for expected value.
- `generate_json_report(...)`: Canonical JSON serialization.
- `generate_executive_report(...)`: Executive summary inventory report.

---

## 8. NON-NEGOTIABLE COMPLIANCE AUDIT

The `goat.statistics` subsystem contains:
- ZERO broker code
- ZERO execution logic
- ZERO portfolio allocation logic
- ZERO risk sizing
- ZERO order placement
- ZERO market prediction
- ZERO signal generation
- ZERO technical indicators
- ZERO strategy rules
- ZERO experiment/evidence/hypothesis mutation

It strictly appends immutable statistical conclusions and scientific decisions.
