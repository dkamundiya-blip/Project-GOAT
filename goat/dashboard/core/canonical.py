"""
Project GOAT v1.0 — Dashboard Canonical Hashing & Identifiers
"""

import hashlib
import json
from typing import Any, Dict


def serialize_canonical_json(data: Dict[str, Any]) -> str:
    """Serialize dictionary to deterministic canonical JSON string."""
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def compute_dashboard_session_id(host: str, port: int, start_time: str) -> str:
    """Compute deterministic SHA-256 ID prefix DSH_ for dashboard session."""
    payload = {"host": host, "port": port, "start_time": start_time}
    digest = hashlib.sha256(serialize_canonical_json(payload).encode("utf-8")).hexdigest()[:16].upper()
    return f"DSH_{digest}"


def compute_telemetry_frame_id(channel: str, timestamp: str, sequence: int) -> str:
    """Compute deterministic SHA-256 ID prefix DTR_ for telemetry frame."""
    payload = {"channel": channel, "sequence": sequence, "timestamp": timestamp}
    digest = hashlib.sha256(serialize_canonical_json(payload).encode("utf-8")).hexdigest()[:16].upper()
    return f"DTR_{digest}"


def compute_ws_connection_id(client_id: str, connect_time: str) -> str:
    """Compute deterministic SHA-256 ID prefix DWS_ for WebSocket connection."""
    payload = {"client_id": client_id, "connect_time": connect_time}
    digest = hashlib.sha256(serialize_canonical_json(payload).encode("utf-8")).hexdigest()[:16].upper()
    return f"DWS_{digest}"


def compute_api_payload_id(route: str, timestamp: str, status_code: int) -> str:
    """Compute deterministic SHA-256 ID prefix DAP_ for API response payload."""
    payload = {"route": route, "status_code": status_code, "timestamp": timestamp}
    digest = hashlib.sha256(serialize_canonical_json(payload).encode("utf-8")).hexdigest()[:16].upper()
    return f"DAP_{digest}"
