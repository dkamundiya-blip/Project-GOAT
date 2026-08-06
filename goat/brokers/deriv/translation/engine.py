"""
Project GOAT v0.8 — Deriv Translation Engine

Bi-directional translation layer converting between GOAT canonical models
(BrokerOrderIntent, BrokerAccount, MarketTick, MarketCandle) and raw Deriv WebSocket JSON payloads.
Raw Deriv payloads NEVER escape past this translation boundary.
"""

from __future__ import annotations

import datetime
from typing import Any

from goat.brokers.core.canonical import compute_account_id
from goat.brokers.core.enums import OrderSide
from goat.brokers.core.models import BrokerAccount, BrokerOrderIntent
from goat.brokers.deriv.core.canonical import (
    compute_deriv_account_snapshot_id,
    compute_deriv_execution_id,
    compute_deriv_order_payload_id,
)
from goat.brokers.deriv.core.enums import DerivContractType, DerivDurationUnit
from goat.brokers.deriv.core.models import (
    DerivAccountSnapshot,
    DerivExecutionResponse,
    DerivOrderPayload,
)
from goat.marketdata.core.canonical import compute_candle_id, compute_tick_id
from goat.marketdata.core.enums import MarketTimeframe
from goat.marketdata.core.models import MarketCandle, MarketTick


class DerivTranslationEngine:
    """Engine responsible for bidirectional translation between GOAT and Deriv protocol payload structures."""

    def translate_order_intent_to_deriv_payload(
        self, intent: BrokerOrderIntent, duration: int = 5, duration_unit: DerivDurationUnit = DerivDurationUnit.TICKS
    ) -> tuple[DerivOrderPayload, dict[str, Any]]:
        """Translate GOAT BrokerOrderIntent to Deriv order payload model and Deriv WebSocket request JSON."""
        contract_type = DerivContractType.RISE if intent.side == OrderSide.BUY else DerivContractType.FALL

        payload_id, canonical_hash = compute_deriv_order_payload_id(intent.intent_id, intent.symbol, intent.quantity)
        deriv_payload_model = DerivOrderPayload(
            payload_id=payload_id,
            intent_id=intent.intent_id,
            symbol=intent.symbol,
            amount=round(intent.quantity, 2),
            contract_type=contract_type,
            duration=duration,
            duration_unit=duration_unit,
            barrier=None,
            metadata={"time_in_force": intent.time_in_force.value},
            canonical_hash=canonical_hash,
        )

        deriv_json_request = {
            "proposal": 1,
            "amount": round(intent.quantity, 2),
            "basis": "stake",
            "contract_type": contract_type.value,
            "currency": "USD",
            "duration": duration,
            "duration_unit": duration_unit.value,
            "symbol": intent.symbol,
            "passthrough": {"intent_id": intent.intent_id, "payload_id": payload_id},
        }

        return deriv_payload_model, deriv_json_request

    def translate_deriv_execution_response(self, deriv_json: dict[str, Any], intent_id: str) -> tuple[DerivExecutionResponse, dict[str, Any]]:
        """Translate raw Deriv buy/buy_contract JSON response into DerivExecutionResponse and canonical execution dict."""
        buy_data = deriv_json.get("buy", deriv_json)
        contract_id = str(buy_data.get("contract_id", "UNKNOWN_CONTRACT"))
        buy_price = float(buy_data.get("buy_price", buy_data.get("price", 0.0)))
        payout = float(buy_data.get("payout", 0.0))
        transaction_id = str(buy_data.get("transaction_id", ""))

        exec_id, canonical_hash = compute_deriv_execution_id(contract_id, buy_price)
        deriv_exec_model = DerivExecutionResponse(
            execution_id=exec_id,
            contract_id=contract_id,
            buy_price=buy_price,
            payout=payout,
            status="PURCHASED" if contract_id != "UNKNOWN_CONTRACT" else "FAILED",
            transaction_id=transaction_id,
            metadata={"intent_id": intent_id},
            canonical_hash=canonical_hash,
        )

        canonical_execution_dict = {
            "execution_id": exec_id,
            "intent_id": intent_id,
            "contract_id": contract_id,
            "fill_price": buy_price,
            "payout": payout,
            "transaction_id": transaction_id,
            "status": "FILLED" if contract_id != "UNKNOWN_CONTRACT" else "REJECTED",
        }

        return deriv_exec_model, canonical_execution_dict

    def translate_deriv_tick_to_market_tick(self, tick_json: dict[str, Any]) -> MarketTick:
        """Translate raw Deriv tick JSON payload into Step 7.0 MarketTick."""
        tick_data = tick_json.get("tick", tick_json)
        symbol = str(tick_data.get("symbol", "R_100"))
        quote = float(tick_data.get("quote", 0.0))
        epoch = int(tick_data.get("epoch", 0))
        sequence = int(tick_data.get("id", epoch))

        iso_ts = datetime.datetime.fromtimestamp(epoch, tz=datetime.timezone.utc).isoformat()
        tick_id, canonical_hash = compute_tick_id(symbol, "DERIV", quote, quote, iso_ts, sequence)

        return MarketTick(
            tick_id=tick_id,
            symbol=symbol,
            broker="DERIV",
            bid=quote,
            ask=quote,
            spread=0.0,
            timestamp=iso_ts,
            sequence_number=sequence,
            source_latency=0.0,
            checksum=canonical_hash,
            metadata={},
            canonical_hash=canonical_hash,
        )

    def translate_deriv_candle_to_market_candle(self, candle_json: dict[str, Any]) -> MarketCandle:
        """Translate raw Deriv ohlc JSON payload into Step 7.0 MarketCandle."""
        ohlc_data = candle_json.get("ohlc", candle_json)
        symbol = str(ohlc_data.get("symbol", "R_100"))
        epoch = int(ohlc_data.get("open_time", ohlc_data.get("epoch", 0)))
        open_price = float(ohlc_data.get("open", 0.0))
        high_price = float(ohlc_data.get("high", 0.0))
        low_price = float(ohlc_data.get("low", 0.0))
        close_price = float(ohlc_data.get("close", 0.0))
        granularity = str(ohlc_data.get("granularity", "60"))

        tf_map = {"60": MarketTimeframe.M1, "300": MarketTimeframe.M5, "3600": MarketTimeframe.H1, "86400": MarketTimeframe.D1}
        timeframe_enum = tf_map.get(granularity, MarketTimeframe.M1)

        open_ts = datetime.datetime.fromtimestamp(epoch, tz=datetime.timezone.utc).isoformat()
        close_ts = datetime.datetime.fromtimestamp(epoch + int(granularity), tz=datetime.timezone.utc).isoformat()

        candle_id, canonical_hash = compute_candle_id(
            symbol, timeframe_enum.value, open_price, high_price, low_price, close_price, open_ts, close_ts
        )

        return MarketCandle(
            candle_id=candle_id,
            symbol=symbol,
            timeframe=timeframe_enum,
            open=open_price,
            high=high_price,
            low=low_price,
            close=close_price,
            volume=0.0,
            open_timestamp=open_ts,
            close_timestamp=close_ts,
            completed=True,
            checksum=canonical_hash,
            metadata={},
            canonical_hash=canonical_hash,
        )

    def translate_deriv_balance_to_account(self, balance_json: dict[str, Any], broker_id: str = "BRK_DERIV") -> tuple[DerivAccountSnapshot, BrokerAccount]:
        """Translate raw Deriv balance response into DerivAccountSnapshot and canonical BrokerAccount model."""
        bal_data = balance_json.get("balance", balance_json)
        login_id = str(bal_data.get("loginid", "CR100001"))
        currency = str(bal_data.get("currency", "USD")).upper()
        balance = float(bal_data.get("balance", 0.0))
        equity = float(bal_data.get("equity", balance))
        margin = float(bal_data.get("margin", 0.0))

        snap_id, snap_hash = compute_deriv_account_snapshot_id(login_id, currency, balance)
        deriv_snapshot = DerivAccountSnapshot(
            snapshot_id=snap_id,
            login_id=login_id,
            currency=currency,
            balance=balance,
            equity=equity,
            margin=margin,
            metadata={},
            canonical_hash=snap_hash,
        )

        acc_id, acc_hash = compute_account_id(broker_id, "REAL", currency)
        broker_account = BrokerAccount(
            account_id=acc_id,
            broker_id=broker_id,
            account_type="REAL",
            account_currency=currency,
            balance=balance,
            equity=max(0.0, equity),
            margin=margin,
            free_margin=max(0.0, equity - margin),
            leverage=100.0,
            metadata={"login_id": login_id},
            canonical_hash=acc_hash,
        )

        return deriv_snapshot, broker_account
