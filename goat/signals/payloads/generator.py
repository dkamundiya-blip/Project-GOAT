"""
Project GOAT v0.7 — Signal Payload Generator

Generates deterministic SignalPayload models formatted for distribution targets:
- JSON, MARKDOWN, NOTIFICATION, WEBHOOK, TELEGRAM, EMAIL, PUSH
- Includes complete SHA-256 checksums and scientific metadata
"""

from __future__ import annotations

import json
from typing import Any

from goat.research.edge.canonical import compute_canonical_sha256
from goat.signals.core.canonical import (
    compute_canonical_sha256 as compute_sha256,
    compute_payload_id,
)
from goat.signals.core.enums import PayloadFormat
from goat.signals.core.models import SignalPayload, TradingSignal


class SignalPayloadGenerator:
    """Generator formatting deterministic SignalPayload objects for notification and adapter consumers."""

    def generate_payload(
        self,
        signal: TradingSignal,
        payload_format: PayloadFormat,
        notification_version: str = "1.0.0",
    ) -> SignalPayload:
        """Generate a deterministic SignalPayload formatted for a target consumer.

        Args:
            signal: Target TradingSignal model.
            payload_format: Target format enum (JSON, MARKDOWN, TELEGRAM, etc.).
            notification_version: Schema version string (default "1.0.0").

        Returns:
            SignalPayload model.
        """
        payload_id, _ = compute_payload_id(signal.signal_id, payload_format.value)

        # Build comprehensive payload data structure
        payload_data: dict[str, Any] = {
            "signal_id": signal.signal_id,
            "instrument": signal.instrument,
            "direction": signal.direction.value,
            "entry_price": signal.entry_price,
            "stop_loss": signal.stop_loss,
            "take_profit": signal.take_profit,
            "recommended_lot_size": signal.recommended_lot_size,
            "minimum_lot_size": signal.minimum_lot_size,
            "risk_percentage": signal.risk_percentage,
            "monetary_risk": signal.monetary_risk,
            "monetary_reward": signal.monetary_reward,
            "risk_reward_ratio": signal.risk_reward_ratio,
            "scientific_confidence": signal.scientific_confidence,
            "qualification_status": signal.qualification_status,
            "validation_status": signal.validation_status,
            "qualification_id": signal.qualification_id,
            "simulation_id": signal.simulation_result_id,
            "composite_id": signal.composite_id,
            "regime_id": signal.regime_id,
            "generation_timestamp": signal.generation_timestamp,
            "expiration_timestamp": signal.expiration_timestamp,
            "replay_reference": signal.replay_reference,
            "audit_reference": signal.audit_reference,
        }

        # Calculate payload SHA-256 checksum
        checksum = compute_canonical_sha256(payload_data).upper()
        payload_data["checksum"] = checksum

        if payload_format == PayloadFormat.MARKDOWN:
            payload_data["rendered_markdown"] = (
                f"# TRADING SIGNAL: `{signal.instrument}` ({signal.direction.value})\n"
                f"- **Entry Price**: `{signal.entry_price:.5f}`\n"
                f"- **Stop Loss**: `{signal.stop_loss:.5f}` | **Take Profit**: `{signal.take_profit:.5f}`\n"
                f"- **Recommended Lots**: `{signal.recommended_lot_size:.2f}`\n"
                f"- **Monetary Risk**: `${signal.monetary_risk:,.2f}` | **Reward**: `${signal.monetary_reward:,.2f}`\n"
                f"- **R:R Ratio**: `{signal.risk_reward_ratio:.2f}` | **Confidence**: `{signal.scientific_confidence:.2f}`\n"
                f"- **Replay Reference**: `{signal.replay_reference}`\n"
            )

        payload = {
            "checksum": checksum,
            "notification_version": notification_version,
            "payload_format": payload_format.value,
            "payload_id": payload_id,
            "signal_id": signal.signal_id,
        }
        canonical_hash = compute_sha256(payload).upper()

        return SignalPayload(
            payload_id=payload_id,
            signal_id=signal.signal_id,
            notification_version=notification_version,
            payload_format=payload_format,
            payload_data=payload_data,
            checksum=checksum,
            metadata={"format": payload_format.value},
            canonical_hash=canonical_hash,
        )
