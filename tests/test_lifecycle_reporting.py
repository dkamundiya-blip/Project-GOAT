"""
Project GOAT v0.8 — Step 7.6 Reporting Engine Dedicated Unit Tests
"""

import json

import pytest

from goat.lifecycle.engine import TradeLifecycleEngine


def test_lifecycle_report_to_markdown_and_json():
    engine = TradeLifecycleEngine()
    l1 = engine.create_trade_lifecycle("EXI_1234567890ABCDEF", "EURUSD", "BUY", 1.0, "2026-08-01T00:00:00Z")
    engine.process_order_submitted(l1.lifecycle_id, "2026-08-01T00:00:01Z")

    report = engine.generate_executive_report("2026-08-01T00:00:01Z")

    md = report.to_markdown()
    assert "# GOAT Trade Lifecycle Executive Report" in md

    js_str = report.to_json()
    parsed = json.loads(js_str)
    assert parsed["reconciliation_status"] in {"RECONCILED", "DISCREPANCIES"}
    assert parsed["summary"]["total_trades"] == 1
