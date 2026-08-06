"""
Project GOAT v0.8 — Deriv Account Engine

Parses raw Deriv balance and account payload updates into DerivAccountSnapshot
and canonical Step 7.2 BrokerAccount models.
"""

from __future__ import annotations

from typing import Any

from goat.brokers.core.models import BrokerAccount
from goat.brokers.deriv.core.models import DerivAccountSnapshot
from goat.brokers.deriv.translation.engine import DerivTranslationEngine


class DerivAccountEngine:
    """Engine managing Deriv account state translation and snapshot tracking."""

    def __init__(self, broker_id: str = "BRK_DERIV", translation_engine: DerivTranslationEngine | None = None):
        self.broker_id = broker_id.strip()
        self.translator = translation_engine or DerivTranslationEngine()
        self._last_snapshot: DerivAccountSnapshot | None = None
        self._last_broker_account: BrokerAccount | None = None

    def process_balance_response(self, balance_json: dict[str, Any]) -> tuple[DerivAccountSnapshot, BrokerAccount]:
        """Process Deriv balance payload into snapshot and canonical BrokerAccount model."""
        snapshot, account = self.translator.translate_deriv_balance_to_account(balance_json, self.broker_id)
        self._last_snapshot = snapshot
        self._last_broker_account = account
        return snapshot, account

    def get_latest_account(self) -> BrokerAccount | None:
        """Retrieve latest parsed BrokerAccount snapshot."""
        return self._last_broker_account
