"""
Project GOAT Phase 5 — SQLite Feature Repository & Database Initializer

Provides high-performance, indexed SQLite storage implementation for the Feature Store.
"""

from __future__ import annotations

import json
from pathlib import Path
import sqlite3
import threading
from typing import Sequence

from goat.feature_engineering.models.feature_vector import FeatureVector
from goat.feature_engineering.persistence.interfaces import IFeatureRepository


def init_feature_store_db(conn_or_path: sqlite3.Connection | str | Path) -> sqlite3.Connection:
    """Initialize SQLite database tables and indices for Phase 5 Feature Store."""
    if isinstance(conn_or_path, (str, Path)):
        path_str = str(conn_or_path)
        if path_str != ":memory:":
            Path(path_str).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(path_str, check_same_thread=False)
    else:
        conn = conn_or_path

    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS engineered_feature_vectors (
                vector_id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                version TEXT NOT NULL,
                features_json TEXT NOT NULL,
                checksum TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_feat_sym_tf_ts ON engineered_feature_vectors (symbol, timeframe, timestamp);"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_feat_ts ON engineered_feature_vectors (timestamp);"
        )

    return conn


class SQLiteFeatureRepository(IFeatureRepository):
    """SQLite implementation of IFeatureRepository."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self._lock = threading.RLock()

    def save_vector(self, vector: FeatureVector) -> None:
        with self._lock, self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO engineered_feature_vectors (
                    vector_id, symbol, timeframe, timestamp, version,
                    features_json, checksum, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    vector.vector_id,
                    vector.symbol,
                    vector.timeframe,
                    vector.timestamp,
                    vector.version,
                    json.dumps(vector.features, sort_keys=True),
                    vector.checksum,
                    json.dumps(vector.metadata, sort_keys=True),
                    vector.canonical_hash,
                ),
            )

    def save_vectors(self, vectors: Sequence[FeatureVector]) -> None:
        if not vectors:
            return
        data = [
            (
                v.vector_id,
                v.symbol,
                v.timeframe,
                v.timestamp,
                v.version,
                json.dumps(v.features, sort_keys=True),
                v.checksum,
                json.dumps(v.metadata, sort_keys=True),
                v.canonical_hash,
            )
            for v in vectors
        ]
        with self._lock, self.conn:
            self.conn.executemany(
                """
                INSERT OR REPLACE INTO engineered_feature_vectors (
                    vector_id, symbol, timeframe, timestamp, version,
                    features_json, checksum, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                data,
            )

    def get_recent_vectors(self, symbol: str, timeframe: str, limit: int = 100) -> list[FeatureVector]:
        with self._lock:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                SELECT vector_id, symbol, timeframe, timestamp, version,
                       features_json, checksum, metadata_json, canonical_hash
                FROM (
                    SELECT vector_id, symbol, timeframe, timestamp, version,
                           features_json, checksum, metadata_json, canonical_hash
                    FROM engineered_feature_vectors
                    WHERE symbol = ? AND timeframe = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ) ORDER BY timestamp ASC;
                """,
                (symbol.upper(), timeframe.lower(), limit),
            )
            rows = cursor.fetchall()
            return [
                FeatureVector(
                    vector_id=r[0],
                    symbol=r[1],
                    timeframe=r[2],
                    timestamp=r[3],
                    version=r[4],
                    features=json.loads(r[5]),
                    checksum=r[6],
                    metadata=json.loads(r[7]),
                    canonical_hash=r[8],
                )
                for r in rows
            ]

    def get_latest_vector(self, symbol: str, timeframe: str) -> FeatureVector | None:
        vectors = self.get_recent_vectors(symbol, timeframe, limit=1)
        return vectors[0] if vectors else None

    def get_vectors_range(self, symbol: str, timeframe: str, start_iso: str, end_iso: str) -> list[FeatureVector]:
        with self._lock:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                SELECT vector_id, symbol, timeframe, timestamp, version,
                       features_json, checksum, metadata_json, canonical_hash
                FROM engineered_feature_vectors
                WHERE symbol = ? AND timeframe = ? AND timestamp >= ? AND timestamp <= ?
                ORDER BY timestamp ASC;
                """,
                (symbol.upper(), timeframe.lower(), start_iso, end_iso),
            )
            rows = cursor.fetchall()
            return [
                FeatureVector(
                    vector_id=r[0],
                    symbol=r[1],
                    timeframe=r[2],
                    timestamp=r[3],
                    version=r[4],
                    features=json.loads(r[5]),
                    checksum=r[6],
                    metadata=json.loads(r[7]),
                    canonical_hash=r[8],
                )
                for r in rows
            ]

    def count(self, symbol: str | None = None, timeframe: str | None = None) -> int:
        with self._lock:
            cursor = self.conn.cursor()
            if symbol and timeframe:
                cursor.execute(
                    "SELECT COUNT(*) FROM engineered_feature_vectors WHERE symbol = ? AND timeframe = ?;",
                    (symbol.upper(), timeframe.lower()),
                )
            elif symbol:
                cursor.execute(
                    "SELECT COUNT(*) FROM engineered_feature_vectors WHERE symbol = ?;",
                    (symbol.upper(),),
                )
            else:
                cursor.execute("SELECT COUNT(*) FROM engineered_feature_vectors;")
            return cursor.fetchone()[0]
