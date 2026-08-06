"""
Project GOAT v0.8 — Broker Persistence Repositories

Provides SQLite repositories enforcing foreign keys (PRAGMA foreign_keys = ON),
round-trip serialization, and query methods for:
- BrokerRepository
- ConnectionRepository
- AccountRepository
- OrderIntentRepository
- ErrorRepository
- BrokerReportRepository
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from goat.brokers.core.enums import (
    BrokerType,
    ConnectionStatus,
    OrderSide,
    OrderType,
    TimeInForce,
)
from goat.brokers.core.models import (
    BrokerAccount,
    BrokerConnection,
    BrokerOrderIntent,
    BrokerProfile,
)
from goat.brokers.errors.framework import BrokerErrorModel


def init_brokers_db(db_path: str | Path) -> sqlite3.Connection:
    """Initialize SQLite database for Broker Abstraction Framework with PRAGMA foreign_keys = ON."""
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")

    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS broker_profiles (
                broker_id TEXT PRIMARY KEY,
                broker_name TEXT NOT NULL,
                broker_type TEXT NOT NULL,
                api_version TEXT NOT NULL,
                supported_assets_json TEXT NOT NULL,
                supported_order_types_json TEXT NOT NULL,
                supports_streaming INTEGER NOT NULL,
                supports_positions INTEGER NOT NULL,
                supports_history INTEGER NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS broker_connections (
                connection_id TEXT PRIMARY KEY,
                broker_id TEXT NOT NULL,
                status TEXT NOT NULL,
                connected_at TEXT NOT NULL,
                disconnected_at TEXT,
                heartbeat_timestamp TEXT NOT NULL,
                latency_ms REAL NOT NULL,
                reconnect_attempts INTEGER NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL,
                FOREIGN KEY (broker_id) REFERENCES broker_profiles(broker_id) ON DELETE CASCADE
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS broker_accounts (
                account_id TEXT PRIMARY KEY,
                broker_id TEXT NOT NULL,
                account_type TEXT NOT NULL,
                account_currency TEXT NOT NULL,
                balance REAL NOT NULL,
                equity REAL NOT NULL,
                margin REAL NOT NULL,
                free_margin REAL NOT NULL,
                leverage REAL NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL,
                FOREIGN KEY (broker_id) REFERENCES broker_profiles(broker_id) ON DELETE CASCADE
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS broker_order_intents (
                intent_id TEXT PRIMARY KEY,
                broker_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                quantity REAL NOT NULL,
                order_type TEXT NOT NULL,
                time_in_force TEXT NOT NULL,
                stop_loss REAL,
                take_profit REAL,
                comment TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL,
                FOREIGN KEY (broker_id) REFERENCES broker_profiles(broker_id) ON DELETE CASCADE
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS broker_errors (
                error_id TEXT PRIMARY KEY,
                code TEXT NOT NULL,
                category TEXT NOT NULL,
                message TEXT NOT NULL,
                explanation TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS broker_reports (
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


class BrokerRepository:
    """SQLite repository for BrokerProfile persistence."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def save(self, profile: BrokerProfile) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO broker_profiles (
                    broker_id, broker_name, broker_type, api_version, supported_assets_json,
                    supported_order_types_json, supports_streaming, supports_positions,
                    supports_history, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    profile.broker_id,
                    profile.broker_name,
                    profile.broker_type.value,
                    profile.api_version,
                    json.dumps(profile.supported_assets),
                    json.dumps([o.value for o in profile.supported_order_types]),
                    1 if profile.supports_streaming else 0,
                    1 if profile.supports_positions else 0,
                    1 if profile.supports_history else 0,
                    json.dumps(profile.metadata, sort_keys=True),
                    profile.canonical_hash,
                ),
            )

    def get_by_id(self, broker_id: str) -> BrokerProfile | None:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM broker_profiles WHERE broker_id = ?;", (broker_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return BrokerProfile(
            broker_id=row[0],
            broker_name=row[1],
            broker_type=BrokerType(row[2]),
            api_version=row[3],
            supported_assets=json.loads(row[4]),
            supported_order_types=[OrderType(o) for o in json.loads(row[5])],
            supports_streaming=bool(row[6]),
            supports_positions=bool(row[7]),
            supports_history=bool(row[8]),
            metadata=json.loads(row[9]),
            canonical_hash=row[10],
        )


class ConnectionRepository:
    """SQLite repository for BrokerConnection persistence."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def save(self, connection: BrokerConnection) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO broker_connections (
                    connection_id, broker_id, status, connected_at, disconnected_at,
                    heartbeat_timestamp, latency_ms, reconnect_attempts, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    connection.connection_id,
                    connection.broker_id,
                    connection.status.value,
                    connection.connected_at,
                    connection.disconnected_at,
                    connection.heartbeat_timestamp,
                    connection.latency_ms,
                    connection.reconnect_attempts,
                    json.dumps(connection.metadata, sort_keys=True),
                    connection.canonical_hash,
                ),
            )

    def get_by_id(self, connection_id: str) -> BrokerConnection | None:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM broker_connections WHERE connection_id = ?;", (connection_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return BrokerConnection(
            connection_id=row[0],
            broker_id=row[1],
            status=ConnectionStatus(row[2]),
            connected_at=row[3],
            disconnected_at=row[4],
            heartbeat_timestamp=row[5],
            latency_ms=row[6],
            reconnect_attempts=row[7],
            metadata=json.loads(row[8]),
            canonical_hash=row[9],
        )


class AccountRepository:
    """SQLite repository for BrokerAccount persistence."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def save(self, account: BrokerAccount) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO broker_accounts (
                    account_id, broker_id, account_type, account_currency, balance,
                    equity, margin, free_margin, leverage, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    account.account_id,
                    account.broker_id,
                    account.account_type,
                    account.account_currency,
                    account.balance,
                    account.equity,
                    account.margin,
                    account.free_margin,
                    account.leverage,
                    json.dumps(account.metadata, sort_keys=True),
                    account.canonical_hash,
                ),
            )

    def get_by_id(self, account_id: str) -> BrokerAccount | None:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM broker_accounts WHERE account_id = ?;", (account_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return BrokerAccount(
            account_id=row[0],
            broker_id=row[1],
            account_type=row[2],
            account_currency=row[3],
            balance=row[4],
            equity=row[5],
            margin=row[6],
            free_margin=row[7],
            leverage=row[8],
            metadata=json.loads(row[9]),
            canonical_hash=row[10],
        )


class OrderIntentRepository:
    """SQLite repository for BrokerOrderIntent persistence."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def save(self, intent: BrokerOrderIntent) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO broker_order_intents (
                    intent_id, broker_id, symbol, side, quantity, order_type,
                    time_in_force, stop_loss, take_profit, comment, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    intent.intent_id,
                    intent.broker_id,
                    intent.symbol,
                    intent.side.value,
                    intent.quantity,
                    intent.order_type.value,
                    intent.time_in_force.value,
                    intent.stop_loss,
                    intent.take_profit,
                    intent.comment,
                    json.dumps(intent.metadata, sort_keys=True),
                    intent.canonical_hash,
                ),
            )

    def get_by_id(self, intent_id: str) -> BrokerOrderIntent | None:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM broker_order_intents WHERE intent_id = ?;", (intent_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return BrokerOrderIntent(
            intent_id=row[0],
            broker_id=row[1],
            symbol=row[2],
            side=OrderSide(row[3]),
            quantity=row[4],
            order_type=OrderType(row[5]),
            time_in_force=TimeInForce(row[6]),
            stop_loss=row[7],
            take_profit=row[8],
            comment=row[9],
            metadata=json.loads(row[10]),
            canonical_hash=row[11],
        )


class ErrorRepository:
    """SQLite repository for BrokerErrorModel persistence."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def save(self, error: BrokerErrorModel) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO broker_errors (
                    error_id, code, category, message, explanation, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    error.error_id,
                    error.code,
                    error.category,
                    error.message,
                    error.explanation,
                    json.dumps(error.metadata, sort_keys=True),
                    error.canonical_hash,
                ),
            )

    def get_by_id(self, error_id: str) -> BrokerErrorModel | None:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM broker_errors WHERE error_id = ?;", (error_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return BrokerErrorModel(
            error_id=row[0],
            code=row[1],
            category=row[2],
            message=row[3],
            explanation=row[4],
            metadata=json.loads(row[5]),
            canonical_hash=row[6],
        )


class BrokerReportRepository:
    """SQLite repository for storing generated Broker reports."""

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
                INSERT OR REPLACE INTO broker_reports (
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
