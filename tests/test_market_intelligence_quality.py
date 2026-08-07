"""
Project GOAT Phase 4 — Unit Tests for Data Quality Engine
"""

import pytest

from goat.market_intelligence.models import QualityIssueReason
from goat.market_intelligence.quality import DataQualityEngine


def test_data_quality_valid_tick():
    engine = DataQualityEngine()
    valid_payload = {
        "symbol": "VOLATILITY_100",
        "price": 4532.30,
        "bid": 4532.10,
        "ask": 4532.50,
        "timestamp": "2026-08-07T12:00:00+00:00",
        "sequence_number": 1,
        "latency_ms": 15.0,
    }
    res = engine.evaluate_tick(valid_payload)
    assert res.passed is True
    assert len(res.issues) == 0


def test_data_quality_negative_spread():
    engine = DataQualityEngine()
    invalid_payload = {
        "symbol": "VOLATILITY_100",
        "bid": 4532.50,
        "ask": 4532.10,  # Ask < Bid (Negative spread)
        "price": 4532.30,
        "timestamp": "2026-08-07T12:00:00+00:00",
        "sequence_number": 1,
    }
    res = engine.evaluate_tick(invalid_payload)
    assert res.passed is False
    assert any(i.reason == QualityIssueReason.NEGATIVE_SPREAD for i in res.issues)


def test_data_quality_impossible_price():
    engine = DataQualityEngine()
    invalid_payload = {
        "symbol": "VOLATILITY_100",
        "price": -100.0,  # Non-positive price
        "timestamp": "2026-08-07T12:00:00+00:00",
        "sequence_number": 1,
    }
    res = engine.evaluate_tick(invalid_payload)
    assert res.passed is False
    assert any(i.reason == QualityIssueReason.IMPOSSIBLE_PRICE for i in res.issues)


def test_data_quality_out_of_order_sequence():
    engine = DataQualityEngine()
    t1 = {
        "symbol": "VOLATILITY_100",
        "price": 100.0,
        "timestamp": "2026-08-07T12:00:00+00:00",
        "sequence_number": 10,
    }
    t2 = {
        "symbol": "VOLATILITY_100",
        "price": 100.1,
        "timestamp": "2026-08-07T12:00:01+00:00",
        "sequence_number": 5,  # Sequence regressed from 10 to 5
    }
    assert engine.evaluate_tick(t1).passed is True
    res2 = engine.evaluate_tick(t2)
    assert res2.passed is False
    assert any(i.reason == QualityIssueReason.OUT_OF_ORDER_TICK for i in res2.issues)


def test_data_quality_report_generation():
    engine = DataQualityEngine()
    for seq in range(1, 11):
        engine.evaluate_tick({
            "symbol": "VOLATILITY_100",
            "price": 100.0 + seq * 0.1,
            "timestamp": f"2026-08-07T12:00:{seq:02d}+00:00",
            "sequence_number": seq,
        })
    # Add one rejected payload
    engine.evaluate_tick({
        "symbol": "VOLATILITY_100",
        "price": -50.0,
        "timestamp": "2026-08-07T12:01:00+00:00",
        "sequence_number": 12,
    })

    report = engine.generate_report("VOLATILITY_100")
    assert report.total_ticks_checked == 11
    assert report.valid_ticks_count == 10
    assert report.rejected_ticks_count == 1
    assert report.pass_rate < 1.0
