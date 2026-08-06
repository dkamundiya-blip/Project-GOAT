"""
Project GOAT v0.9 — Reporting Generators for Edge Promotion & Retirement Governance Subsystem
"""

from typing import Any

from goat.governance.core.canonical import serialize_canonical_json
from goat.governance.core.models import (
    EdgeCandidate,
    GovernanceAudit,
    GovernanceDecision,
    GovernanceSummary,
    PromotionAssessment,
    RetirementAssessment,
)


def generate_promotion_report(assessment: PromotionAssessment) -> str:
    """Generate Markdown report for a PromotionAssessment."""
    status_str = "PROMOTABLE" if assessment.is_promotable else "NOT PROMOTABLE"

    return f"""# EDGE PROMOTION ASSESSMENT REPORT

**Assessment ID**: `{assessment.assessment_id}`  
**Edge ID**: `{assessment.edge_id}`  
**Hypothesis ID**: `{assessment.hypothesis_id}`  
**Promotion Status**: `{status_str}`  
**Timestamp**: {assessment.timestamp}  
**Canonical Hash**: `{assessment.canonical_hash}`  

---

### Criteria Verification Inventory
- **Hypothesis Verified**: `{assessment.is_hypothesis_passed}`  
- **Evidence Chain Complete**: `{assessment.is_evidence_complete}`  
- **Experiment Execution Complete**: `{assessment.is_experiment_complete}`  
- **Statistical Evaluation Supported**: `{assessment.is_statistics_complete}`  
- **Live Validation Passed**: `{assessment.is_live_validation_complete}`  
- **Constitutional Compliance**: `{assessment.is_constitution_satisfied}`  
- **PRSP v1.0 Compliance**: `{assessment.is_research_protocol_satisfied}`  

---

### Evaluation Commentary
{assessment.assessment_notes}
"""


def generate_retirement_report(assessment: RetirementAssessment) -> str:
    """Generate Markdown report for a RetirementAssessment."""
    rec_str = "RETIREMENT RECOMMENDED" if assessment.is_retirement_recommended else "RETAIN IN PRODUCTION / TESTING"

    return f"""# EDGE RETIREMENT ASSESSMENT REPORT

**Assessment ID**: `{assessment.assessment_id}`  
**Edge ID**: `{assessment.edge_id}`  
**Hypothesis ID**: `{assessment.hypothesis_id}`  
**Retirement Recommendation**: `{rec_str}`  
**Timestamp**: {assessment.timestamp}  
**Canonical Hash**: `{assessment.canonical_hash}`  

---

### Risk & Degradation Metrics
- **Expectancy Degradation Ratio**: `{assessment.expectancy_degradation:.4f}`  
- **Statistical Confidence Decline**: `{assessment.confidence_decline:.4f}`  
- **Structural Market Shift**: `{assessment.structural_shift_detected}`  
- **Amendment No.001 Violation**: `{assessment.amendment_001_violation}`  

---

### Evaluation Commentary
{assessment.assessment_notes}
"""


def generate_governance_decision_report(decision: GovernanceDecision) -> str:
    """Generate Markdown report for a GovernanceDecision."""
    return f"""# CONSTITUTIONAL GOVERNANCE DECISION REPORT

**Decision ID**: `{decision.decision_id}`  
**Edge ID**: `{decision.edge_id}`  
**Hypothesis ID**: `{decision.hypothesis_id}`  
**Binding Decision**: `{decision.decision.value}`  
**Governance Reason**: `{decision.reason.value}`  
**Authorizer**: {decision.authorizer}  
**Timestamp**: {decision.timestamp}  
**Canonical Hash**: `{decision.canonical_hash}`  

---

### Constitutional & Scientific Justification
{decision.rationale}
"""


def generate_audit_report(audit: GovernanceAudit) -> str:
    """Generate Markdown report for a GovernanceAudit."""
    exp_str = "VERIFIED (100% EXPLAINABLE)" if audit.is_explainable else "UNEXPLAINABLE"
    rep_str = "VERIFIED (100% REPLAYABLE)" if audit.is_replayable else "NON-REPLAYABLE"

    return f"""# GOVERNANCE AUDIT TRAIL REPORT

**Audit ID**: `{audit.audit_id}`  
**Decision ID**: `{audit.decision_id}`  
**Edge ID**: `{audit.edge_id}`  
**Hypothesis ID**: `{audit.hypothesis_id}`  
**Experiment ID**: `{audit.experiment_id}`  
**Evaluation ID**: `{audit.evaluation_id}`  
**Live Validation Session ID**: `{audit.validation_session_id}`  
**Explainability**: `{exp_str}`  
**Replayability**: `{rep_str}`  
**Audit Operator**: {audit.operator}  
**Timestamp**: {audit.timestamp}  
**Canonical Hash**: `{audit.canonical_hash}`  
"""


def generate_json_report(entity: Any) -> str:
    """Generate canonical JSON report for any domain entity."""
    return serialize_canonical_json(entity)


def generate_executive_report(summary: GovernanceSummary, recent_decisions: list[GovernanceDecision]) -> str:
    """Generate Executive Summary Report for Edge Governance Subsystem."""
    st_rows = "\n".join([f"| `{k}` | {v} |" for k, v in summary.status_counts.items()]) or "| None | 0 |"
    dec_rows = "\n".join([f"| `{k}` | {v} |" for k, v in summary.decision_counts.items()]) or "| None | 0 |"
    rsn_rows = "\n".join([f"| `{k}` | {v} |" for k, v in summary.reason_counts.items()]) or "| None | 0 |"

    rec_rows = []
    for d in recent_decisions:
        rec_rows.append(f"| `{d.decision_id}` | `{d.edge_id}` | `{d.decision.value}` | `{d.reason.value}` | {d.timestamp} |")
    rec_table = "\n".join(rec_rows) if rec_rows else "| None | - | - | - | - |"

    return f"""# PROJECT GOAT — EDGE GOVERNANCE EXECUTIVE REPORT

**Total Edges**: `{summary.total_edges}`  
**Total Decisions**: `{summary.total_decisions}`  
**Snapshot ID**: `{summary.summary_id}`  
**Timestamp**: {summary.timestamp}  

---

## Executive Overview
Project GOAT Version 0.9 Edge Promotion & Retirement Governance Engine acts as the constitutional decision-making authority over all quantitative trading edges. Decisions are governed strictly by SHA-256 fingerprinted evidence, free from human discretion or parameter tuning.

---

### Edge Lifecycle Status Breakdown
| Status | Count |
| :--- | :--- |
{st_rows}

---

### Binding Decision Outcomes Breakdown
| Decision Outcome | Count |
| :--- | :--- |
{dec_rows}

---

### Governance Reason Categories Breakdown
| Rationale Category | Count |
| :--- | :--- |
{rsn_rows}

---

## Recent Governance Decisions Inventory
| Decision ID | Edge ID | Decision | Reason Category | Timestamp |
| :--- | :--- | :--- | :--- | :--- |
{rec_table}
"""
