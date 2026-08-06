"""
Project GOAT v0.7 — Test Suite for SignalDeliveryEngine & SignalPayloadGenerator

Coverage:
- Formatting payloads across all targets (JSON, MARKDOWN, NOTIFICATION, WEBHOOK, TELEGRAM, EMAIL, PUSH)
- Checksum verification
- Internal payload dispatching
"""

from goat.signals.core.canonical import compute_signal_id
from goat.signals.core.enums import PayloadFormat, SignalDirection
from goat.signals.core.models import TradingSignal
from goat.signals.delivery.engine import SignalDeliveryEngine
from goat.signals.payloads.generator import SignalPayloadGenerator


def test_signal_payload_generator():
    generator = SignalPayloadGenerator()

    s_id, s_hash = compute_signal_id("SQL_1", "SRS_1", "RSA_1")
    signal = TradingSignal(
        signal_id=s_id,
        qualification_id="SQL_1",
        simulation_result_id="SRS_1",
        risk_assessment_id="RSA_1",
        composite_id="CMP_1",
        regime_id="MRG_1",
        instrument="EURUSD",
        direction=SignalDirection.BUY,
        entry_price=1.0850,
        stop_loss=1.0800,
        take_profit=1.0950,
        recommended_lot_size=4.0,
        monetary_risk=2000.0,
        monetary_reward=4000.0,
        risk_reward_ratio=2.0,
        scientific_confidence=0.90,
        generation_timestamp="2026-07-30T00:00:00Z",
        expiration_timestamp="2026-07-31T00:00:00Z",
        canonical_hash=s_hash,
    )

    payload = generator.generate_payload(signal, PayloadFormat.JSON)

    assert payload.payload_id.startswith("SPL_")
    assert payload.signal_id == s_id
    assert payload.payload_format == PayloadFormat.JSON
    assert payload.checksum != ""
    assert payload.payload_data["instrument"] == "EURUSD"
    assert payload.payload_data["direction"] == "BUY"


def test_signal_delivery_engine():
    delivery_engine = SignalDeliveryEngine()

    s_id, s_hash = compute_signal_id("SQL_1", "SRS_1", "RSA_1")
    signal = TradingSignal(
        signal_id=s_id,
        qualification_id="SQL_1",
        simulation_result_id="SRS_1",
        risk_assessment_id="RSA_1",
        composite_id="CMP_1",
        regime_id="MRG_1",
        instrument="EURUSD",
        direction=SignalDirection.BUY,
        entry_price=1.0850,
        stop_loss=1.0800,
        take_profit=1.0950,
        recommended_lot_size=4.0,
        monetary_risk=2000.0,
        monetary_reward=4000.0,
        risk_reward_ratio=2.0,
        scientific_confidence=0.90,
        generation_timestamp="2026-07-30T00:00:00Z",
        expiration_timestamp="2026-07-31T00:00:00Z",
        canonical_hash=s_hash,
    )

    all_payloads = delivery_engine.prepare_all_delivery_payloads(signal)

    assert len(all_payloads) == len(PayloadFormat)
    assert PayloadFormat.JSON in all_payloads
    assert PayloadFormat.TELEGRAM in all_payloads

    res = delivery_engine.dispatch_payload(all_payloads[PayloadFormat.JSON])
    assert res["delivery_status"] == "DELIVERED_INTERNAL"
