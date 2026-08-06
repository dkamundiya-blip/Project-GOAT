"""
Project GOAT v0.8 — Step 7.9 Reporting Engine Dedicated Unit Tests
"""

import json

import pytest

from goat.archive.core.enums import ArchiveEntityType, ArchiveSubsystemOrigin
from goat.archive.engine import ArchiveEngine


def test_archive_executive_report_generation():
    engine = ArchiveEngine()
    ts = "2026-08-01T00:00:00Z"

    engine.ingest_record(
        source_subsystem=ArchiveSubsystemOrigin.EXECUTION_ENGINE,
        entity_type=ArchiveEntityType.EXECUTION,
        entity_id="EXC_101",
        payload={"volume": 1.0},
        timestamp=ts,
    )

    report = engine.generate_executive_report(ts)

    md = report.to_markdown()
    assert "# GOAT Institutional Research Archive Executive Report" in md

    js_str = report.to_json()
    parsed = json.loads(js_str)
    assert parsed["summary"]["total_records"] == 1
