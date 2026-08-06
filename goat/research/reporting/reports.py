"""
Project GOAT v0.9 — Reporting Generators for Research & Hypothesis Engine
"""

from goat.research.core.canonical import serialize_canonical_json
from goat.research.core.models import (
    HypothesisApproval,
    HypothesisRegistrySummary,
    HypothesisRevision,
    HypothesisValidation,
    ScientificHypothesis,
)
from goat.research.registry.engine import ScientificHypothesisRegistry


def generate_markdown_report(hypothesis: ScientificHypothesis) -> str:
    """Generate Markdown report for a ScientificHypothesis."""
    ind_vars = "\n".join([f"- {v}" for v in hypothesis.independent_variables]) or "- None"
    dep_vars = "\n".join([f"- {v}" for v in hypothesis.dependent_variables]) or "- None"
    assumptions = "\n".join([f"- {a}" for a in hypothesis.assumptions]) or "- None"
    success_criteria = "\n".join([f"- {s}" for s in hypothesis.success_criteria]) or "- None"
    failure_criteria = "\n".join([f"- {f}" for f in hypothesis.failure_criteria]) or "- None"
    tags_str = ", ".join(hypothesis.tags) if hypothesis.tags else "None"

    return f"""# SCIENTIFIC HYPOTHESIS REPORT
## {hypothesis.title}

**Hypothesis ID**: `{hypothesis.hypothesis_id}`  
**Author**: {hypothesis.author}  
**Created**: {hypothesis.created_timestamp}  
**Updated**: {hypothesis.updated_timestamp}  
**Status**: `{hypothesis.status.value}` | **Priority**: `{hypothesis.priority.value}` | **Evidence Level**: `{hypothesis.evidence_level.value}`  
**Revision Number**: `{hypothesis.revision_number}`  
**Canonical Hash**: `{hypothesis.canonical_hash}`  
**Tags**: {tags_str}  

---

### 1. Scientific Research Question
> {hypothesis.research_question}

---

### 2. Hypotheses Statements
- **Null Hypothesis ($H_0$)**: {hypothesis.null_hypothesis}
- **Alternative Hypothesis ($H_1$)**: {hypothesis.alternative_hypothesis}

---

### 3. Expected Behaviour & Structural Mechanism
{hypothesis.expected_behaviour}

---

### 4. Variables
#### Independent Variables:
{ind_vars}

#### Dependent Variables:
{dep_vars}

---

### 5. Assumptions
{assumptions}

---

### 6. Tail Risk Statement
{hypothesis.risk_statement}

---

### 7. Success & Failure Criteria
#### Success Criteria:
{success_criteria}

#### Failure Criteria:
{failure_criteria}
"""


def generate_json_report(hypothesis: ScientificHypothesis) -> str:
    """Generate canonical JSON report for a ScientificHypothesis."""
    return serialize_canonical_json(hypothesis)


def generate_validation_report(validation: HypothesisValidation) -> str:
    """Generate Markdown report for a HypothesisValidation outcome."""
    outcome_str = "PASSED (VALID)" if validation.is_valid else "FAILED (INVALID)"
    errors_str = "\n".join([f"- ERROR: {e}" for e in validation.validation_errors]) or "- None"
    warnings_str = "\n".join([f"- WARNING: {w}" for w in validation.validation_warnings]) or "- None"

    rule_rows = []
    for r in validation.validation_rule_results:
        status_icon = "PASS" if r.get("passed") else "FAIL"
        rule_rows.append(f"| {r.get('rule_id')} | {status_icon} | {len(r.get('errors', []))} errors |")
    rules_table = "\n".join(rule_rows) or "| N/A | N/A | N/A |"

    return f"""# HYPOTHESIS VALIDATION REPORT

**Validation ID**: `{validation.validation_id}`  
**Target Hypothesis ID**: `{validation.hypothesis_id}`  
**Reviewer**: {validation.reviewer}  
**Timestamp**: {validation.timestamp}  
**Outcome**: `{outcome_str}`  
**Canonical Hash**: `{validation.canonical_hash}`  

---

### Rule Evaluation Details
| Rule ID | Status | Details |
| :--- | :--- | :--- |
{rules_table}

---

### Validation Errors
{errors_str}

---

### Validation Warnings
{warnings_str}
"""


def generate_registry_summary_report(summary: HypothesisRegistrySummary) -> str:
    """Generate Markdown report for HypothesisRegistrySummary."""
    status_rows = "\n".join([f"| {k} | {v} |" for k, v in summary.status_counts.items()])
    priority_rows = "\n".join([f"| {k} | {v} |" for k, v in summary.priority_counts.items()])
    evidence_rows = "\n".join([f"| {k} | {v} |" for k, v in summary.evidence_level_counts.items()])

    return f"""# HYPOTHESIS REGISTRY SUMMARY REPORT

**Summary ID**: `{summary.summary_id}`  
**Timestamp**: {summary.timestamp}  
**Total Registered Hypotheses**: `{summary.total_hypotheses}`  
**Canonical Hash**: `{summary.canonical_hash}`  

---

### Status Breakdown
| Status | Count |
| :--- | :--- |
{status_rows}

---

### Priority Breakdown
| Priority | Count |
| :--- | :--- |
{priority_rows}

---

### Evidence Level Breakdown
| Evidence Level | Count |
| :--- | :--- |
{evidence_rows}
"""


def generate_executive_report(registry: ScientificHypothesisRegistry) -> str:
    """Generate high-level Executive Markdown Report for the registry."""
    summary = registry.generate_summary()
    hypotheses = registry.list_all_hypotheses()

    hyp_rows = []
    for h in hypotheses:
        hyp_rows.append(
            f"| `{h.hypothesis_id}` | {h.title} | `{h.status.value}` | `{h.priority.value}` | `{h.evidence_level.value}` | Rev `{h.revision_number}` |"
        )
    hyp_table = "\n".join(hyp_rows) if hyp_rows else "| None | No hypotheses registered | - | - | - | - |"

    return f"""# PROJECT GOAT — SCIENTIFIC HYPOTHESIS REGISTRY EXECUTIVE REPORT

**Total Hypotheses**: `{summary.total_hypotheses}`  
**Snapshot ID**: `{summary.summary_id}`  
**Timestamp**: {summary.timestamp}  

---

## Executive Summary
Project GOAT Version 0.9 Hypothesis Registry contains `{summary.total_hypotheses}` registered quantitative research hypotheses. All hypotheses are fingerprinted with SHA-256 canonical digests and tracked under PRSP v1.0 governance standards.

---

## Registered Hypotheses Inventory
| Hypothesis ID | Title | Status | Priority | Evidence Level | Revision |
| :--- | :--- | :--- | :--- | :--- | :--- |
{hyp_table}
"""
