"""
Project GOAT v0.8 — Canonical Hashing & Deterministic ID Generation for Archive Vault

Provides deterministic SHA-256 hash computation and prefix-based ID generation for:
- ArchiveRecord (ARC_<HEX16>)
- ArchiveBatch (ABT_<HEX16>)
- ReplayRequest (RRQ_<HEX16>)
- ReplaySession (RPS_<HEX16>)
- ReplayCheckpoint (RCP_<HEX16>)
- SnapshotManifest (SNP_<HEX16>)
- ArchiveStatistics (AST_<HEX16>)
- ArchiveSummary (ASM_<HEX16>)
"""

from goat.research.edge.canonical import compute_canonical_sha256


def compute_archive_id(
    source_subsystem: str,
    entity_type: str,
    entity_id: str,
    timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    payload = {
        "entity_id": str(entity_id).strip(),
        "entity_type": str(entity_type).strip().upper(),
        "source_subsystem": str(source_subsystem).strip().upper(),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"ARC_{digest[:16].upper()}", digest.upper()


def compute_batch_id(
    record_count: int,
    timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    payload = {
        "record_count": int(record_count),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"ABT_{digest[:16].upper()}", digest.upper()


def compute_replay_request_id(
    start_time: str,
    end_time: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    payload = {
        "end_time": str(end_time).strip(),
        "start_time": str(start_time).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"RRQ_{digest[:16].upper()}", digest.upper()


def compute_replay_session_id(
    request_id: str,
    start_time: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    payload = {
        "request_id": str(request_id).strip(),
        "start_time": str(start_time).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"RPS_{digest[:16].upper()}", digest.upper()


def compute_replay_checkpoint_id(
    sequence: int,
    record_id: str,
    timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    payload = {
        "record_id": str(record_id).strip(),
        "sequence": int(sequence),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"RCP_{digest[:16].upper()}", digest.upper()


def compute_snapshot_manifest_id(
    snapshot_type: str,
    timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    payload = {
        "snapshot_type": str(snapshot_type).strip().upper(),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"SNP_{digest[:16].upper()}", digest.upper()


def compute_statistics_id(
    total_records: int,
    timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    payload = {
        "timestamp": str(timestamp).strip(),
        "total_records": int(total_records),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"AST_{digest[:16].upper()}", digest.upper()


def compute_summary_id(
    total_records: int,
    timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    payload = {
        "timestamp": str(timestamp).strip(),
        "total_records": int(total_records),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"ASM_{digest[:16].upper()}", digest.upper()
