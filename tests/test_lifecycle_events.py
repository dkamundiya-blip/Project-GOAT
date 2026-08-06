"""
Project GOAT v0.8 — Step 7.6 Trade Event Engine Dedicated Unit Tests
"""

import pytest

from goat.lifecycle.core.enums import TradeEventType
from goat.lifecycle.events.engine import TradeEventEngine


def test_trade_event_engine_record_15_events():
    engine = TradeEventEngine()
    lid = "TRL_1234567890ABCDEF"

    all_event_types = list(TradeEventType)
    assert len(all_event_types) == 15

    for idx, evt_type in enumerate(all_event_types):
        evt = engine.record_event(
            lifecycle_id=lid,
            event_type=evt_type,
            timestamp=f"2026-08-01T00:{idx:02d}:00Z",
            details=f"Event {evt_type.value} recorded",
        )
        assert evt.event_type == evt_type
        assert evt.lifecycle_id == lid

    events = engine.get_events_for_lifecycle(lid)
    assert len(events) == 15
    assert [e.event_type for e in events] == all_event_types


@pytest.mark.parametrize("idx", range(100))
def test_trade_event_append_only_integrity(idx):
    engine = TradeEventEngine()
    lid = f"TRL_{idx:016X}"

    e1 = engine.record_event(lid, TradeEventType.ORDER_SUBMITTED, "2026-08-01T00:00:00Z")
    e2 = engine.record_event(lid, TradeEventType.BROKER_ACCEPTED, "2026-08-01T00:01:00Z")

    events = engine.get_events_for_lifecycle(lid)
    assert len(events) == 2
    assert events[0].event_id == e1.event_id
    assert events[1].event_id == e2.event_id
