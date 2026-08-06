"""
Project GOAT v1.0 — Test Suite: Dashboard Backend Telemetry Collector
"""

import pytest

from goat.dashboard.core.enums import TelemetryChannel
from goat.dashboard.telemetry.collector import SystemTelemetryCollector

CHANNELS = list(TelemetryChannel)
CLIENT_COUNTS = [0, 1, 5, 10, 50, 100]


@pytest.mark.parametrize("clients", CLIENT_COUNTS)
def test_system_telemetry_collector_matrix(clients):
    collector = SystemTelemetryCollector()
    frame1 = collector.collect_system_telemetry(active_ws_clients=clients)
    assert frame1.channel == TelemetryChannel.SYSTEM
    assert frame1.sequence == 1
    assert frame1.payload["active_ws_clients"] == clients
    assert frame1.frame_id.startswith("DTR_")

    frame2 = collector.collect_system_telemetry(active_ws_clients=clients)
    assert frame2.sequence == 2


@pytest.mark.parametrize("channel", CHANNELS)
@pytest.mark.parametrize("idx", list(range(10)))
def test_custom_telemetry_frame_matrix(channel, idx):
    collector = SystemTelemetryCollector()
    frame = collector.create_custom_telemetry_frame(channel=channel, payload={"idx": idx})
    assert frame.channel == channel
    assert frame.sequence == 1
    assert frame.payload["idx"] == idx
