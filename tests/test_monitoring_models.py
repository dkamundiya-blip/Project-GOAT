"""
Project GOAT v0.8 — Step 7.8 Operational Monitoring Models Dedicated Unit Tests
"""

import pytest
from pydantic import ValidationError

from goat.monitoring.core.canonical import (
    compute_alert_id,
    compute_heartbeat_id,
    compute_reliability_id,
    compute_subsystem_health_id,
    compute_summary_id,
    compute_system_health_id,
    compute_telemetry_id,
    compute_watchdog_id,
)
from goat.monitoring.core.enums import AlertLevel, HealthLevel, SubsystemName
from goat.monitoring.core.models import (
    HealthAlert,
    HeartbeatRecord,
    MonitoringSummary,
    ReliabilityAssessment,
    SubsystemHealth,
    SystemHealth,
    TelemetrySnapshot,
    WatchdogStatus,
)


def test_canonical_id_prefixes():
    syh_id, syh_hash = compute_system_health_id("HEALTHY", "2026-08-01T00:00:00Z")
    assert syh_id.startswith("SYH_")
    assert len(syh_id) == 20
    assert len(syh_hash) == 64

    sbh_id, sbh_hash = compute_subsystem_health_id("EXECUTION_ENGINE", "HEALTHY", "2026-08-01T00:00:00Z")
    assert sbh_id.startswith("SBH_")
    assert len(sbh_id) == 20

    hbt_id, hbt_hash = compute_heartbeat_id("LIVE_MARKET_DATA", 1, "2026-08-01T00:00:00Z")
    assert hbt_id.startswith("HBT_")
    assert len(hbt_id) == 20

    hal_id, hal_hash = compute_alert_id("BROKER_ADAPTER", "WARNING", "2026-08-01T00:00:00Z")
    assert hal_id.startswith("HAL_")
    assert len(hal_id) == 20

    tel_id, tel_hash = compute_telemetry_id(12.5, 45.2, "2026-08-01T00:00:00Z")
    assert tel_id.startswith("TEL_")
    assert len(tel_id) == 20

    ras_id, ras_hash = compute_reliability_id(99.9, "2026-08-01T00:00:00Z")
    assert ras_id.startswith("RAS_")
    assert len(ras_id) == 20

    wdg_id, wdg_hash = compute_watchdog_id(7, 0, "2026-08-01T00:00:00Z")
    assert wdg_id.startswith("WDG_")
    assert len(wdg_id) == 20

    msm_id, msm_hash = compute_summary_id(100, "2026-08-01T00:00:00Z")
    assert msm_id.startswith("MSM_")
    assert len(msm_id) == 20


def test_monitoring_model_immutability():
    syh_id, syh_hash = compute_system_health_id("HEALTHY", "2026-08-01T00:00:00Z")
    health = SystemHealth(
        health_id=syh_id,
        overall_health=HealthLevel.HEALTHY,
        timestamp="2026-08-01T00:00:00Z",
        canonical_hash=syh_hash,
    )

    with pytest.raises(ValidationError):
        health.overall_health = HealthLevel.CRITICAL


def test_monitoring_model_extra_forbid():
    syh_id, syh_hash = compute_system_health_id("HEALTHY", "2026-08-01T00:00:00Z")
    with pytest.raises(ValidationError):
        SystemHealth(
            health_id=syh_id,
            overall_health=HealthLevel.HEALTHY,
            timestamp="2026-08-01T00:00:00Z",
            canonical_hash=syh_hash,
            extra_field="invalid",
        )


@pytest.mark.parametrize("idx", range(150))
def test_monitoring_model_serialization_matrix(idx):
    hbt_id, hbt_hash = compute_heartbeat_id("LIVE_MARKET_DATA", idx, f"2026-08-01T00:{idx % 60:02d}:00Z")
    heartbeat = HeartbeatRecord(
        heartbeat_id=hbt_id,
        subsystem_name=SubsystemName.LIVE_MARKET_DATA,
        sequence=idx,
        timestamp=f"2026-08-01T00:{idx % 60:02d}:00Z",
        canonical_hash=hbt_hash,
    )
    json_str = heartbeat.model_dump_json()
    reloaded = HeartbeatRecord.model_validate_json(json_str)
    assert reloaded == heartbeat
