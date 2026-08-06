"""
Project GOAT v0.8 — Broker Order Intent Engine

Validates order intent structure, supported order types, supported assets,
and required parameters without executing trades or communicating with brokers.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from goat.brokers.contracts.registry import BrokerCapabilityRegistry
from goat.brokers.core.models import BrokerOrderIntent, BrokerProfile


class IntentValidationResult(BaseModel):
    """Immutable validation result emitted by BrokerOrderIntentEngine."""

    valid: bool = Field(..., description="True if order intent satisfies capability and structural rules")
    intent_id: str = Field(..., description="Target order intent ID")
    broker_id: str = Field(..., description="Target broker profile ID")
    explanation: str = Field(..., description="Deterministic explanation of validation result")

    class Config:
        frozen = True
        extra = "forbid"


class BrokerOrderIntentEngine:
    """Engine responsible for deterministic structural validation of order intents."""

    def __init__(self, registry: BrokerCapabilityRegistry | None = None):
        self.registry = registry or BrokerCapabilityRegistry()

    def validate_intent(self, intent: BrokerOrderIntent, profile: BrokerProfile | None = None) -> IntentValidationResult:
        """Validate order intent against broker profile capabilities and structural rules."""
        broker_id = intent.broker_id

        # 1. Structural Checks
        if intent.quantity <= 0.0:
            return IntentValidationResult(
                valid=False,
                intent_id=intent.intent_id,
                broker_id=broker_id,
                explanation=f"Invalid order volume: quantity must be positive ({intent.quantity})",
            )

        if intent.stop_loss is not None and intent.stop_loss <= 0.0:
            return IntentValidationResult(
                valid=False,
                intent_id=intent.intent_id,
                broker_id=broker_id,
                explanation=f"Invalid stop loss level: stop_loss must be positive if set ({intent.stop_loss})",
            )

        if intent.take_profit is not None and intent.take_profit <= 0.0:
            return IntentValidationResult(
                valid=False,
                intent_id=intent.intent_id,
                broker_id=broker_id,
                explanation=f"Invalid take profit level: take_profit must be positive if set ({intent.take_profit})",
            )

        # 2. Capability Registry Checks
        target_profile = profile or self.registry.get_profile(broker_id)
        if target_profile:
            if not self.registry.supports_asset(broker_id, intent.symbol):
                return IntentValidationResult(
                    valid=False,
                    intent_id=intent.intent_id,
                    broker_id=broker_id,
                    explanation=f"Unsupported asset symbol '{intent.symbol}' for broker '{broker_id}'",
                )

            if not self.registry.supports_order_type(broker_id, intent.order_type):
                return IntentValidationResult(
                    valid=False,
                    intent_id=intent.intent_id,
                    broker_id=broker_id,
                    explanation=f"Unsupported order type '{intent.order_type.value}' for broker '{broker_id}'",
                )

        return IntentValidationResult(
            valid=True,
            intent_id=intent.intent_id,
            broker_id=broker_id,
            explanation=f"Order intent {intent.intent_id} satisfied all structural and capability validation rules",
        )
