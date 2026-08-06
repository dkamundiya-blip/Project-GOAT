"""
Project GOAT v0.8 — Canonical Hashing & Deterministic ID Generation for Monitoring Engine

Provides deterministic SHA-256 hash computation and prefix-based ID generation for:
- SystemHealth (SYH_<HEX16>)
- SubsystemHealth (SBH_<HEX16>)
- HeartbeatRecord (HBT_<HEX16>)
- HealthAlert (HAL_<HEX16>)
- TelemetrySnapshot (TEL_<HEX16>)
- ReliabilityAssessment (RAS_<HEX16>)
- WatchdogStatus (WDG_<HEX16>)
- MonitoringSummary (MSM_<HEX16>)
"""

from goat.research.edge.canonical import compute_canonical_sha256


def compute_system_health_id(
    overall_health: str,
    timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    payload = {
        "overall_health": str(overall_health).strip().upper(),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"SYH_{digest[:16].upper()}", digest.upper()


def compute_subsystem_health_id(
    subsystem_name: str,
    health_level: str,
    timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    payload = {
        "health_level": str(health_level).strip().upper(),
        "subsystem_name": str(subsystem_name).strip().upper(),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"SBH_{digest[:16].upper()}", digest.upper()


def compute_heartbeat_id(
    subsystem_name: str,
    sequence: int,
    timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    payload = {
        "sequence": int(sequence),
        "subsystem_name": str(subsystem_name).strip().upper(),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"HBT_{digest[:16].upper()}", digest.upper()


def compute_alert_id(
    subsystem_name: str,
    alert_level: str,
    timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    payload = {
        "alert_level": str(alert_level).strip().upper(),
        "subsystem_name": str(subsystem_name).strip().upper(),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"HAL_{digest[:16].upper()}", digest.upper()


def compute_telemetry_id(
    cpu_usage: float,
    memory_usage: float,
    timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    payload = {
        "cpu_usage": round(float(cpu_usage), 4),
        "memory_usage": round(float(memory_usage), 4),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"TEL_{digest[:16].upper()}", digest.upper()


def compute_reliability_id(
    reliability_score: float,
    timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    payload = {
        "reliability_score": round(float(reliability_score), 4),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"RAS_{digest[:16].upper()}", digest.upper()


def compute_watchdog_id(
    active_count: int,
    dead_count: int,
    timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    payload = {
        "active_count": int(active_count),
        "dead_count": int(dead_count),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"WDG_{digest[:16].upper()}", digest.upper()


def compute_summary_id(
    total_heartbeats: int,
    timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    payload = {
        "timestamp": str(timestamp).strip(),
        "total_heartbeats": int(total_heartbeats),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"MSM_{digest[:16].upper()}", digest.upper()
