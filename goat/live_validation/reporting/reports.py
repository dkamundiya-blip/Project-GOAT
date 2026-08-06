"""
Project GOAT v0.9 — Reporting Generators for Controlled Live Scientific Validation Subsystem
"""

from typing import Any

from goat.live_validation.core.canonical import serialize_canonical_json
from goat.live_validation.core.models import (
    LiveValidationCandidate,
    ValidationDecision,
    ValidationObservation,
    ValidationSession,
    ValidationSummary,
)


def generate_eligibility_report(candidate: LiveValidationCandidate) -> str:
    """Generate Markdown report for a LiveValidationCandidate."""
    ev_ids_str = "\n".join([f"- `{eid}`" for eid in candidate.evidence_ids]) or "- None"

    return f"""# LIVE VALIDATION CANDIDATE ELIGIBILITY REPORT

**Candidate ID**: `{candidate.candidate_id}`  
**Hypothesis ID**: `{candidate.hypothesis_id}`  
**Evaluation ID**: `{candidate.evaluation_id}`  
**Experiment ID**: `{candidate.experiment_id}`  
**Replay ID**: `{candidate.replay_id or 'N/A'}`  
**Status**: `{candidate.status.value}`  
**Eligibility Score**: `{candidate.eligibility_score:.2f}`  
**Created**: {candidate.created_timestamp}  
**Canonical Hash**: `{candidate.canonical_hash}`  

---

### Associated Evidence References ({len(candidate.evidence_ids)})
{ev_ids_str}
"""


def generate_validation_report(session: ValidationSession, observations: list[ValidationObservation]) -> str:
    """Generate Markdown report for a ValidationSession and its observations."""
    obs_count = len(observations)
    avg_slippage = (sum(o.slippage for o in observations) / float(obs_count)) if obs_count > 0 else 0.0
    avg_latency = (sum(o.latency_ms for o in observations) / float(obs_count)) if obs_count > 0 else 0.0

    return f"""# CONTROLLED LIVE VALIDATION SESSION REPORT

**Session ID**: `{session.session_id}`  
**Candidate ID**: `{session.candidate_id}`  
**Hypothesis ID**: `{session.hypothesis_id}`  
**Status**: `{session.status.value}`  
**Monitoring Status**: `{session.monitoring_status.value}`  
**Start Timestamp**: {session.start_timestamp}  
**End Timestamp**: {session.end_timestamp or 'ACTIVE'}  
**Total Observations**: `{session.total_observations}`  
**Operator**: {session.operator}  
**Canonical Hash**: `{session.canonical_hash}`  

---

### Key Execution Metrics
- **Recorded Observations**: `{obs_count}`  
- **Average Slippage**: `{avg_slippage:.6f}`  
- **Average Latency**: `{avg_latency:.2f} ms`  
"""


def generate_monitoring_report(session_id: str, observations: list[ValidationObservation]) -> str:
    """Generate Markdown report for execution quality monitoring."""
    obs_count = len(observations)
    avg_slippage = (sum(abs(o.slippage) for o in observations) / float(obs_count)) if obs_count > 0 else 0.0
    avg_spread = (sum(o.spread for o in observations) / float(obs_count)) if obs_count > 0 else 0.0
    avg_latency = (sum(o.latency_ms for o in observations) / float(obs_count)) if obs_count > 0 else 0.0
    avg_fill = (sum(o.fill_ratio for o in observations) / float(obs_count)) if obs_count > 0 else 1.0

    return f"""# EXECUTION QUALITY MONITORING REPORT

**Session ID**: `{session_id}`  
**Observation Sample Size**: `{obs_count}`  

---

### Real-Time Health Metrics
- **Mean Absolute Slippage**: `{avg_slippage:.6f}`  
- **Mean Market Spread**: `{avg_spread:.6f}`  
- **Mean Latency**: `{avg_latency:.2f} ms`  
- **Mean Fill Consistency Ratio**: `{avg_fill * 100:.2f}%`  
"""


def generate_decision_report(decision: ValidationDecision) -> str:
    """Generate Markdown report for a ValidationDecision."""
    return f"""# VALIDATION SCIENTIFIC DECISION REPORT

**Decision ID**: `{decision.decision_id}`  
**Session ID**: `{decision.session_id}`  
**Candidate ID**: `{decision.candidate_id}`  
**Decision Outcome**: `{decision.decision.value}`  
**Authorizer**: {decision.authorizer}  
**Timestamp**: {decision.timestamp}  
**Canonical Hash**: `{decision.canonical_hash}`  

---

### Decision Rationale & Justification
{decision.rationale}
"""


def generate_json_report(entity: Any) -> str:
    """Generate canonical JSON report for any domain entity."""
    return serialize_canonical_json(entity)


def generate_executive_report(summary: ValidationSummary, recent_sessions: list[ValidationSession]) -> str:
    """Generate Executive Summary Report for Live Validation Subsystem."""
    st_rows = "\n".join([f"| `{k}` | {v} |" for k, v in summary.status_counts.items()]) or "| None | 0 |"
    dec_rows = "\n".join([f"| `{k}` | {v} |" for k, v in summary.decision_counts.items()]) or "| None | 0 |"

    rec_rows = []
    for s in recent_sessions:
        rec_rows.append(f"| `{s.session_id}` | `{s.candidate_id}` | `{s.status.value}` | `{s.monitoring_status.value}` | {s.total_observations} |")
    rec_table = "\n".join(rec_rows) if rec_rows else "| None | - | - | - | - |"

    return f"""# PROJECT GOAT — CONTROLLED LIVE VALIDATION EXECUTIVE REPORT

**Total Candidates**: `{summary.total_candidates}`  
**Total Sessions**: `{summary.total_sessions}`  
**Total Observations**: `{summary.total_observations}`  
**Snapshot ID**: `{summary.summary_id}`  
**Timestamp**: {summary.timestamp}  

---

## Executive Overview
Project GOAT Version 0.9 Controlled Live Scientific Validation Engine monitors active live research sessions under real market execution conditions. All observations, candidate qualifications, and scientific recommendations are SHA-256 fingerprinted and auditable.

---

### Session Status Breakdown
| Status | Count |
| :--- | :--- |
{st_rows}

---

### Validation Decision Breakdown
| Outcome | Count |
| :--- | :--- |
{dec_rows}

---

## Recent Live Validation Sessions
| Session ID | Candidate ID | Status | Monitoring | Observations |
| :--- | :--- | :--- | :--- | :--- |
{rec_table}
"""
