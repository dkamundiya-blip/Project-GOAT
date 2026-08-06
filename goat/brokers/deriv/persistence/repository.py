"""
Project GOAT v0.8 — Deriv Storage Repositories

SQLite repositories for persisting Deriv models with WAL mode,
foreign keys (PRAGMA foreign_keys = ON), and deterministic serialization.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from goat.brokers.core.enums import ConnectionStatus
from goat.brokers.deriv.core.enums import DerivContractType, DerivDurationUnit
from goat.brokers.deriv.core.models import (
    DerivAccountSnapshot,
    DerivAuthentication,
    DerivExecutionResponse,
    DerivHeartbeat,
    DerivMarketSubscription,
    DerivOrderPayload,
    DerivSession,
)


def init_deriv_db(db_path: str | Path) -> sqlite3.Connection:
    """Initialize SQLite database for Deriv Production Adapter with foreign keys enabled."""
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")

    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS deriv_sessions (
                session_id TEXT PRIMARY KEY,
                broker_id TEXT NOT NULL,
                status TEXT NOT NULL,
                server_time TEXT NOT NULL,
                ping_ms REAL NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS deriv_authentications (
                auth_id TEXT PRIMARY KEY,
                app_id INTEGER NOT NULL,
                token_hash TEXT NOT NULL,
                is_authenticated INTEGER NOT NULL,
                user_id TEXT NOT NULL,
                email TEXT NOT NULL,
                currency TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS deriv_account_snapshots (
                snapshot_id TEXT PRIMARY KEY,
                login_id TEXT NOT NULL,
                currency TEXT NOT NULL,
                balance REAL NOT NULL,
                equity REAL NOT NULL,
                margin REAL NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS deriv_subscriptions (
                subscription_id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                request_id INTEGER NOT NULL,
                is_active INTEGER NOT NULL,
                stream_id TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS deriv_order_payloads (
                payload_id TEXT PRIMARY KEY,
                intent_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                amount REAL NOT NULL,
                contract_type TEXT NOT NULL,
                duration INTEGER NOT NULL,
                duration_unit TEXT NOT NULL,
                barrier TEXT,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS deriv_executions (
                execution_id TEXT PRIMARY KEY,
                contract_id TEXT NOT NULL,
                buy_price REAL NOT NULL,
                payout REAL NOT NULL,
                status TEXT NOT NULL,
                transaction_id TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS deriv_heartbeats (
                heartbeat_id TEXT PRIMARY KEY,
                ping_timestamp TEXT NOT NULL,
                pong_timestamp TEXT NOT NULL,
                roundtrip_ms REAL NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS deriv_reports (
                report_id TEXT PRIMARY KEY,
                report_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                markdown_content TEXT NOT NULL,
                json_content TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
            """
        )

    return conn


class SessionRepository:
    """SQLite repository for DerivSession."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def save(self, session: DerivSession) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO deriv_sessions (
                    session_id, broker_id, status, server_time, ping_ms, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    session.session_id,
                    session.broker_id,
                    session.status.value,
                    session.server_time,
                    session.ping_ms,
                    json.dumps(session.metadata, sort_keys=True),
                    session.canonical_hash,
                ),
            )

    def get_by_id(self, session_id: str) -> DerivSession | None:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM deriv_sessions WHERE session_id = ?;", (session_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return DerivSession(
            session_id=row[0],
            broker_id=row[1],
            status=ConnectionStatus(row[2]),
            server_time=row[3],
            ping_ms=row[4],
            metadata=json.loads(row[5]),
            canonical_hash=row[6],
        )


class AuthenticationRepository:
    """SQLite repository for DerivAuthentication."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def save(self, auth: DerivAuthentication) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO deriv_authentications (
                    auth_id, app_id, token_hash, is_authenticated, user_id, email, currency, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    auth.auth_id,
                    auth.app_id,
                    auth.token_hash,
                    1 if auth.is_authenticated else 0,
                    auth.user_id,
                    auth.email,
                    auth.currency,
                    json.dumps(auth.metadata, sort_keys=True),
                    auth.canonical_hash,
                ),
            )

    def get_by_id(self, auth_id: str) -> DerivAuthentication | None:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM deriv_authentications WHERE auth_id = ?;", (auth_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return DerivAuthentication(
            auth_id=row[0],
            app_id=row[1],
            token_hash=row[2],
            is_authenticated=bool(row[3]),
            user_id=row[4],
            email=row[5],
            currency=row[6],
            metadata=json.loads(row[7]),
            canonical_hash=row[8],
        )


class MarketSubscriptionRepository:
    """SQLite repository for DerivMarketSubscription."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def save(self, sub: DerivMarketSubscription) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO deriv_subscriptions (
                    subscription_id, symbol, request_id, is_active, stream_id, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    sub.subscription_id,
                    sub.symbol,
                    sub.request_id,
                    1 if sub.is_active else 0,
                    sub.stream_id,
                    json.dumps(sub.metadata, sort_keys=True),
                    sub.canonical_hash,
                ),
            )

    def get_by_id(self, subscription_id: str) -> DerivMarketSubscription | None:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM deriv_subscriptions WHERE subscription_id = ?;", (subscription_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return DerivMarketSubscription(
            subscription_id=row[0],
            symbol=row[1],
            request_id=row[2],
            is_active=bool(row[3]),
            stream_id=row[4],
            metadata=json.loads(row[5]),
            canonical_hash=row[6],
        )


class OrderRepository:
    """SQLite repository for DerivOrderPayload."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def save(self, payload: DerivOrderPayload) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO deriv_order_payloads (
                    payload_id, intent_id, symbol, amount, contract_type, duration, duration_unit, barrier, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    payload.payload_id,
                    payload.intent_id,
                    payload.symbol,
                    payload.amount,
                    payload.contract_type.value,
                    payload.duration,
                    payload.duration_unit.value,
                    payload.barrier,
                    json.dumps(payload.metadata, sort_keys=True),
                    payload.canonical_hash,
                ),
            )

    def get_by_id(self, payload_id: str) -> DerivOrderPayload | None:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM deriv_order_payloads WHERE payload_id = ?;", (payload_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return DerivOrderPayload(
            payload_id=row[0],
            intent_id=row[1],
            symbol=row[2],
            amount=row[3],
            contract_type=DerivContractType(row[4]),
            duration=row[5],
            duration_unit=DerivDurationUnit(row[6]),
            barrier=row[7],
            metadata=json.loads(row[8]),
            canonical_hash=row[9],
        )


class ExecutionRepository:
    """SQLite repository for DerivExecutionResponse."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def save(self, execution: DerivExecutionResponse) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO deriv_executions (
                    execution_id, contract_id, buy_price, payout, status, transaction_id, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    execution.execution_id,
                    execution.contract_id,
                    execution.buy_price,
                    execution.payout,
                    execution.status,
                    execution.transaction_id,
                    json.dumps(execution.metadata, sort_keys=True),
                    execution.canonical_hash,
                ),
            )

    def get_by_id(self, execution_id: str) -> DerivExecutionResponse | None:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM deriv_executions WHERE execution_id = ?;", (execution_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return DerivExecutionResponse(
            execution_id=row[0],
            contract_id=row[1],
            buy_price=row[2],
            payout=row[3],
            status=row[4],
            transaction_id=row[5],
            metadata=json.loads(row[6]),
            canonical_hash=row[7],
        )


class HeartbeatRepository:
    """SQLite repository for DerivHeartbeat."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def save(self, hb: DerivHeartbeat) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO deriv_heartbeats (
                    heartbeat_id, ping_timestamp, pong_timestamp, roundtrip_ms, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?);
                """,
                (
                    hb.heartbeat_id,
                    hb.ping_timestamp,
                    hb.pong_timestamp,
                    hb.roundtrip_ms,
                    json.dumps(hb.metadata, sort_keys=True),
                    hb.canonical_hash,
                ),
            )

    def get_by_id(self, heartbeat_id: str) -> DerivHeartbeat | None:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM deriv_heartbeats WHERE heartbeat_id = ?;", (heartbeat_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return DerivHeartbeat(
            heartbeat_id=row[0],
            ping_timestamp=row[1],
            pong_timestamp=row[2],
            roundtrip_ms=row[3],
            metadata=json.loads(row[4]),
            canonical_hash=row[5],
        )


class ReportRepository:
    """SQLite repository for storing generated Deriv reports."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def save_report(
        self,
        report_id: str,
        report_type: str,
        timestamp: str,
        markdown_content: str,
        json_content: str,
        canonical_hash: str,
    ) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO deriv_reports (
                    report_id, report_type, timestamp, markdown_content, json_content, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?);
                """,
                (
                    report_id,
                    report_type,
                    timestamp,
                    markdown_content,
                    json_content,
                    canonical_hash,
                ),
            )
