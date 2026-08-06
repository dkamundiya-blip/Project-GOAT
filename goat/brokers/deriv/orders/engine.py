"""
Project GOAT v0.8 — Deriv Order Engine

Processes BrokerOrderIntent requests, translates them into Deriv order payloads via DerivTranslationEngine,
and processes incoming Deriv execution response payloads into DerivExecutionResponse models.
"""

from __future__ import annotations

from typing import Any

from goat.brokers.core.models import BrokerOrderIntent
from goat.brokers.deriv.core.enums import DerivDurationUnit
from goat.brokers.deriv.core.models import DerivExecutionResponse, DerivOrderPayload
from goat.brokers.deriv.translation.engine import DerivTranslationEngine


class DerivOrderEngine:
    """Engine managing Deriv order translation, proposal building, and purchase execution response mapping."""

    def __init__(self, translation_engine: DerivTranslationEngine | None = None):
        self.translator = translation_engine or DerivTranslationEngine()
        self._payload_history: list[DerivOrderPayload] = []
        self._execution_history: list[DerivExecutionResponse] = []

    def prepare_order_payload(
        self, intent: BrokerOrderIntent, duration: int = 5, duration_unit: DerivDurationUnit = DerivDurationUnit.TICKS
    ) -> tuple[DerivOrderPayload, dict[str, Any]]:
        """Translate BrokerOrderIntent into DerivOrderPayload model and Deriv WebSocket request JSON."""
        payload_model, request_json = self.translator.translate_order_intent_to_deriv_payload(intent, duration, duration_unit)
        self._payload_history.append(payload_model)
        return payload_model, request_json

    def process_execution_response(
        self, deriv_response_json: dict[str, Any], intent_id: str
    ) -> tuple[DerivExecutionResponse, dict[str, Any]]:
        """Process raw Deriv purchase response JSON into DerivExecutionResponse model and canonical execution dict."""
        exec_model, exec_dict = self.translator.translate_deriv_execution_response(deriv_response_json, intent_id)
        self._execution_history.append(exec_model)
        return exec_model, exec_dict

    def get_order_history(self) -> list[DerivOrderPayload]:
        """Retrieve list of prepared order payloads."""
        return list(self._payload_history)

    def get_execution_history(self) -> list[DerivExecutionResponse]:
        """Retrieve list of execution responses."""
        return list(self._execution_history)
