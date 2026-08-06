"""
Project GOAT v0.9 — Reporting Generators for Observation & Evidence Subsystem
"""

from goat.evidence.core.canonical import serialize_canonical_json
from goat.evidence.core.models import (
    EvidenceLink,
    EvidenceRecord,
    EvidenceSummary,
    ObservationCollection,
    ScientificObservation,
)


def generate_observation_report(observation: ScientificObservation) -> str:
    """Generate Markdown report for a ScientificObservation."""
    tags_str = ", ".join(observation.tags) if observation.tags else "None"
    return f"""# SCIENTIFIC OBSERVATION REPORT

**Observation ID**: `{observation.observation_id}`  
**Metric Name**: `{observation.metric_name}`  
**Metric Value**: `{observation.metric_value}` {observation.unit_of_measure}  
**Source**: `{observation.source.value}` | **Category**: `{observation.category.value}`  
**Instrument**: `{observation.instrument or 'N/A'}`  
**Timestamp**: {observation.timestamp}  
**Observer**: {observation.observer_id}  
**Canonical Hash**: `{observation.canonical_hash}`  
**Tags**: {tags_str}  
"""


def generate_evidence_report(record: EvidenceRecord) -> str:
    """Generate Markdown report for an EvidenceRecord."""
    obs_ids_str = "\n".join([f"- `{oid}`" for oid in record.observation_ids]) or "- None"
    tags_str = ", ".join(record.tags) if record.tags else "None"

    return f"""# EVIDENCE RECORD REPORT
## {record.title}

**Evidence ID**: `{record.evidence_id}`  
**Category**: `{record.category.value}` | **Source**: `{record.source.value}`  
**Instrument**: `{record.instrument or 'N/A'}`  
**Timestamp**: {record.timestamp}  
**Canonical Hash**: `{record.canonical_hash}`  
**Tags**: {tags_str}  

---

### Description
{record.description or 'No description provided.'}

---

### Component Scientific Observations ({len(record.observation_ids)})
{obs_ids_str}
"""


def generate_collection_summary_report(collection: ObservationCollection) -> str:
    """Generate Markdown report for an ObservationCollection."""
    obs_ids_str = "\n".join([f"- `{oid}`" for oid in collection.observation_ids]) or "- None"
    tags_str = ", ".join(collection.tags) if collection.tags else "None"

    return f"""# OBSERVATION COLLECTION REPORT
## {collection.collection_name}

**Collection ID**: `{collection.collection_id}`  
**Start Time**: {collection.start_timestamp}  
**End Time**: {collection.end_timestamp}  
**Collector**: {collection.collector_id}  
**Observation Count**: `{len(collection.observation_ids)}`  
**Canonical Hash**: `{collection.canonical_hash}`  
**Tags**: {tags_str}  

---

### Included Observations
{obs_ids_str}
"""


def generate_json_report(entity: Any) -> str:
    """Generate canonical JSON report for any domain entity."""
    return serialize_canonical_json(entity)


def generate_evidence_summary_report(summary: EvidenceSummary) -> str:
    """Generate Markdown report for EvidenceSummary metrics."""
    cat_rows = "\n".join([f"| {k} | {v} |" for k, v in summary.category_counts.items()])
    src_rows = "\n".join([f"| {k} | {v} |" for k, v in summary.source_counts.items()])

    return f"""# EVIDENCE SUBSYSTEM SUMMARY REPORT

**Summary ID**: `{summary.summary_id}`  
**Timestamp**: {summary.timestamp}  
**Total Observations**: `{summary.total_observations}`  
**Total Evidence Records**: `{summary.total_evidence_records}`  
**Total Collections**: `{summary.total_collections}`  
**Total Hypothesis Links**: `{summary.total_links}`  
**Canonical Hash**: `{summary.canonical_hash}`  

---

### Evidence Category Breakdown
| Category | Count |
| :--- | :--- |
{cat_rows}

---

### Observation Source Breakdown
| Source | Count |
| :--- | :--- |
{src_rows}
"""


def generate_executive_report(summary: EvidenceSummary, recent_records: list[EvidenceRecord]) -> str:
    """Generate Executive Markdown Report for Evidence Subsystem."""
    rec_rows = []
    for r in recent_records:
        rec_rows.append(f"| `{r.evidence_id}` | {r.title} | `{r.category.value}` | `{r.instrument or 'N/A'}` | {r.timestamp} |")
    rec_table = "\n".join(rec_rows) if rec_rows else "| None | No evidence compiled | - | - | - |"

    return f"""# PROJECT GOAT — EVIDENCE SUBSYSTEM EXECUTIVE REPORT

**Total Observations**: `{summary.total_observations}`  
**Total Evidence Records**: `{summary.total_evidence_records}`  
**Total Collections**: `{summary.total_collections}`  
**Snapshot ID**: `{summary.summary_id}`  
**Timestamp**: {summary.timestamp}  

---

## Executive Overview
Project GOAT Version 0.9 Evidence Subsystem currently holds `{summary.total_observations}` objective, uninterpreted market observations and `{summary.total_evidence_records}` compiled evidence records. All evidence artifacts are SHA-256 fingerprinted and append-only.

---

## Recent Evidence Records Inventory
| Evidence ID | Title | Category | Instrument | Timestamp |
| :--- | :--- | :--- | :--- | :--- |
{rec_table}
"""
