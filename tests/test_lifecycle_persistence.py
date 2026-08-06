"""
Project GOAT v0.8 — Step 7.6 Persistence Dedicated Unit Tests
"""

import tempfile
from pathlib import Path

import pytest

from goat.lifecycle.core.enums import TradeState
from goat.lifecycle.engine import TradeLifecycleEngine
from goat.lifecycle.persistence.repository import SQLiteLifecycleRepository


def test_sqlite_persistence_roundtrip():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_lifecycle.db"
        engine = TradeLifecycleEngine(db_path=db_path)

        l1 = engine.create_trade_lifecycle("EXI_1234567890ABCDEF", "EURUSD", "BUY", 1.0, "2026-08-01T00:00:00Z")
        engine.process_order_submitted(l1.lifecycle_id, "2026-08-01T00:00:01Z")
        engine.process_broker_accepted(l1.lifecycle_id, "2026-08-01T00:00:02Z")
        engine.process_broker_execution_fill(l1.lifecycle_id, "BO_1001", 1.0850, 1.0, "2026-08-01T00:00:03Z")
        engine.process_position_opened(l1.lifecycle_id, "POS_1234567890ABCDEF", "2026-08-01T00:00:04Z")
        engine.process_complete_close(l1.lifecycle_id, 1.0900, "2026-08-01T01:00:00Z", close_reason="MANUAL")

        # Close engine to flush WAL and release connection lock on Windows
        engine.close()

        # Verify DB records directly
        repo = SQLiteLifecycleRepository(db_path)
        db_l = repo.get_lifecycle(l1.lifecycle_id)
        assert db_l is not None
        assert db_l.current_state == TradeState.CLOSED
        assert db_l.closed_at == "2026-08-01T01:00:00Z"

        db_events = repo.get_events(l1.lifecycle_id)
        assert len(db_events) >= 5

        db_audits = repo.get_audits(l1.lifecycle_id)
        assert len(db_audits) >= 6

        repo.close()
