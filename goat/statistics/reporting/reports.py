"""
Project GOAT v0.9 — Reporting Generators for Statistical Evaluation Subsystem
"""

from goat.statistics.core.canonical import serialize_canonical_json
from goat.statistics.core.models import (
    ConfidenceAssessment,
    EvaluationDecision,
    EvaluationSummary,
    ExpectancyAssessment,
    SignificanceAssessment,
    StatisticalEvaluation,
)


def generate_statistical_report(evaluation: StatisticalEvaluation) -> str:
    """Generate Markdown report for a StatisticalEvaluation."""
    tags_str = ", ".join(evaluation.tags) if evaluation.tags else "None"

    return f"""# STATISTICAL EVALUATION REPORT

**Evaluation ID**: `{evaluation.evaluation_id}`  
**Experiment ID**: `{evaluation.experiment_id}`  
**Hypothesis ID**: `{evaluation.hypothesis_id}`  
**Decision**: `{evaluation.decision.value}`  
**Confidence Level**: `{evaluation.confidence_level}` | **Confidence Rating**: `{evaluation.confidence_rating.value}`  
**P-Value**: `{evaluation.p_value:.6f}` | **Effect Size**: `{evaluation.effect_size:.6f}`  
**Expected Value**: `{evaluation.expected_value:.6f}` | **Sample Size**: `{evaluation.sample_size}`  
**Evaluator**: {evaluation.evaluator}  
**Timestamp**: {evaluation.timestamp}  
**Canonical Hash**: `{evaluation.canonical_hash}`  
**Tags**: {tags_str}  
"""


def generate_confidence_report(confidence: ConfidenceAssessment) -> str:
    """Generate Markdown report for a ConfidenceAssessment."""
    return f"""# CONFIDENCE ASSESSMENT REPORT

**Confidence ID**: `{confidence.confidence_id}`  
**Evaluation ID**: `{confidence.evaluation_id}`  
**Confidence Level**: `{confidence.confidence_level * 100:.1f}%`  
**Confidence Interval**: `[{confidence.lower_bound:.6f}, {confidence.upper_bound:.6f}]`  
**Margin of Error**: `{confidence.margin_of_error:.6f}`  
**Sample Size**: `{confidence.sample_size}`  
**Rating**: `{confidence.confidence_rating.value}`  
**Timestamp**: {confidence.timestamp}  
**Canonical Hash**: `{confidence.canonical_hash}`  
"""


def generate_significance_report(significance: SignificanceAssessment) -> str:
    """Generate Markdown report for a SignificanceAssessment."""
    sig_str = "YES (REJECT H0)" if significance.is_significant else "NO (FAIL TO REJECT H0)"

    return f"""# SIGNIFICANCE ASSESSMENT REPORT

**Significance ID**: `{significance.significance_id}`  
**Evaluation ID**: `{significance.evaluation_id}`  
**P-Value**: `{significance.p_value:.6f}` | **Adjusted P-Value**: `{significance.adjusted_p_value:.6f}`  
**Test Statistic**: `{significance.test_statistic:.6f}`  
**Alpha Threshold**: `{significance.alpha_threshold}`  
**Statistically Significant**: `{sig_str}`  
**Multiple Comparison Correction**: `{significance.multiple_comparison_correction}`  
**Timestamp**: {significance.timestamp}  
**Canonical Hash**: `{significance.canonical_hash}`  
"""


def generate_expectancy_report(expectancy: ExpectancyAssessment) -> str:
    """Generate Markdown report for an ExpectancyAssessment."""
    return f"""# EXPECTANCY ASSESSMENT REPORT

**Expectancy ID**: `{expectancy.expectancy_id}`  
**Evaluation ID**: `{expectancy.evaluation_id}`  
**Mathematical Expectancy**: `{expectancy.expected_value:.6f}` per observation  
**Win Rate**: `{expectancy.win_rate * 100:.2f}%` | **Loss Rate**: `{expectancy.loss_rate * 100:.2f}%`  
**Average Gain**: `{expectancy.average_gain:.6f}` | **Average Loss**: `{expectancy.average_loss:.6f}`  
**Profit Factor**: `{expectancy.profit_factor:.4f}`  
**Sample Size**: `{expectancy.sample_size}`  
**Timestamp**: {expectancy.timestamp}  
**Canonical Hash**: `{expectancy.canonical_hash}`  
"""


def generate_json_report(entity: Any) -> str:
    """Generate canonical JSON report for any domain entity."""
    return serialize_canonical_json(entity)


def generate_executive_report(summary: EvaluationSummary, recent_evaluations: list[StatisticalEvaluation]) -> str:
    """Generate Executive Summary Markdown Report for Statistical Subsystem."""
    dec_rows = "\n".join([f"| `{k}` | {v} |" for k, v in summary.decision_counts.items()]) or "| None | 0 |"
    conf_rows = "\n".join([f"| `{k}` | {v} |" for k, v in summary.confidence_counts.items()]) or "| None | 0 |"

    rec_rows = []
    for e in recent_evaluations:
        rec_rows.append(f"| `{e.evaluation_id}` | `{e.hypothesis_id}` | `{e.decision.value}` | `{e.p_value:.4f}` | `{e.expected_value:.4f}` | {e.timestamp} |")
    rec_table = "\n".join(rec_rows) if rec_rows else "| None | - | - | - | - | - |"

    return f"""# PROJECT GOAT — STATISTICAL EVALUATION EXECUTIVE REPORT

**Total Evaluations**: `{summary.total_evaluations}`  
**Total Decisions**: `{summary.total_decisions}`  
**Snapshot ID**: `{summary.summary_id}`  
**Timestamp**: {summary.timestamp}  

---

## Executive Overview
Project GOAT Version 0.9 Statistical Evaluation Engine has performed `{summary.total_evaluations}` empirical evaluations and issued `{summary.total_decisions}` formal scientific decisions. All conclusions are derived from SHA-256 fingerprinted evidence and statistical procedures.

---

### Decision Distribution Breakdown
| Scientific Decision | Count |
| :--- | :--- |
{dec_rows}

---

### Confidence Rating Breakdown
| Confidence Rating | Count |
| :--- | :--- |
{conf_rows}

---

## Recent Registered Evaluations Inventory
| Evaluation ID | Hypothesis ID | Decision | p-Value | Expectancy | Timestamp |
| :--- | :--- | :--- | :--- | :--- | :--- |
{rec_table}
"""
