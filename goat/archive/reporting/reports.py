"""
Project GOAT v0.8 — Institutional Archive Reporting Engine

Generates canonical Markdown and JSON reports for:
- ArchiveReport
- ReplayReport
- SnapshotReport
- IntegrityReport
- ArchiveStatisticsReport
- ArchiveExecutiveReport

Supports to_markdown() and to_json() formatting.
"""

from __future__ import annotations

import json
from typing import Any

from goat.archive.core.models import (
    ArchiveBatch,
    ArchiveRecord,
    ArchiveStatistics,
    ArchiveSummary,
    ReplayCheckpoint,
    ReplaySession,
    SnapshotManifest,
)


class BaseArchiveReport:
    """Base report class providing to_markdown() and to_json() contract interface."""

    def __init__(self, title: str, markdown_content: str, json_payload: dict[str, Any]):
        self.title = title
        self._markdown = markdown_content
        self._json_payload = json_payload

    def to_markdown(self) -> str:
        return self._markdown

    def to_json(self) -> str:
        return json.dumps(self._json_payload, indent=2, sort_keys=True)

    def get_dict(self) -> dict[str, Any]:
        return dict(self._json_payload)


class ArchiveReport(BaseArchiveReport):
    """Report detailing archived record contents."""
    pass


class ReplayReport(BaseArchiveReport):
    """Report detailing replay session execution logs and checkpoint streams."""
    pass


class SnapshotReport(BaseArchiveReport):
    """Report detailing captured state snapshot manifests."""
    pass


class IntegrityReport(BaseArchiveReport):
    """Report detailing archive hash integrity and cryptographic audit results."""
    pass


class ArchiveStatisticsReport(BaseArchiveReport):
    """Report detailing subsystem record volumes and storage statistics."""
    pass


class ArchiveExecutiveReport(BaseArchiveReport):
    """Executive Report combining archive metrics, replay history, and integrity status."""
    pass


class ArchiveReportEngine:
    """Reporting engine generating structured Markdown and JSON archive reports."""

    def build_archive_report(self, record: ArchiveRecord) -> ArchiveReport:
        json_data = record.model_dump()
        markdown = f"""# GOAT Archive Record Report

- **Archive ID**: `{record.archive_id}`
- **Source Subsystem**: `{record.source_subsystem.value}`
- **Entity Type**: `{record.entity_type.value}`
- **Entity ID**: `{record.entity_id}`
- **Timestamp**: {record.timestamp}

---
*Canonical Hash*: `{record.canonical_hash}`
"""
        return ArchiveReport("Archive Record Report", markdown, json_data)

    def build_replay_report(self, session: ReplaySession, checkpoints: list[ReplayCheckpoint]) -> ReplayReport:
        json_data = {
            "session": session.model_dump(),
            "checkpoints_count": len(checkpoints),
            "checkpoints": [c.model_dump() for c in checkpoints],
        }

        rows = []
        for c in checkpoints[:20]:
            rows.append(f"| `{c.checkpoint_id[:12]}` | {c.sequence} | `{c.record_id[:12]}` | {c.timestamp} |")
        table = "\n".join(rows) if rows else "| None | - | - | - |"

        markdown = f"""# GOAT Deterministic Replay Report

- **Session ID**: `{session.session_id}`
- **Request ID**: `{session.request_id}`
- **Replayed Records**: {session.records_replayed}
- **Status**: `{session.status.value}`

| Checkpoint ID | Sequence | Record ID | Timestamp |
|---|---|---|---|
{table}
"""
        return ReplayReport("Deterministic Replay Report", markdown, json_data)

    def build_integrity_report(self, is_healthy: bool, valid_count: int, invalid_count: int, timestamp: str) -> IntegrityReport:
        json_data = {
            "is_healthy": is_healthy,
            "valid_count": valid_count,
            "invalid_count": invalid_count,
            "timestamp": timestamp,
        }
        status_str = "VERIFIED HEALTHY" if is_healthy else "TAMPER DETECTED"

        markdown = f"""# GOAT Archive Vault Integrity Audit Report

- **Status**: `{status_str}`
- **Timestamp**: {timestamp}
- **Valid Hash Count**: {valid_count}
- **Corrupted / Invalid Count**: {invalid_count}
"""
        return IntegrityReport("Archive Vault Integrity Audit Report", markdown, json_data)

    def build_executive_report(
        self,
        summary: ArchiveSummary,
        recent_records: list[ArchiveRecord],
        sessions: list[ReplaySession],
    ) -> ArchiveExecutiveReport:
        json_data = {
            "summary": summary.model_dump(),
            "recent_records_count": len(recent_records),
            "sessions_count": len(sessions),
        }

        markdown = f"""# GOAT Institutional Research Archive Executive Report

- **Timestamp**: {summary.timestamp}
- **Summary ID**: `{summary.summary_id}`
- **Total Archived Records**: {summary.total_records}
- **Total Replay Sessions**: {summary.total_sessions}
- **Vault Integrity Status**: `{summary.integrity_status}`
"""
        return ArchiveExecutiveReport("Institutional Research Archive Executive Report", markdown, json_data)
