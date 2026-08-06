"""
Project GOAT v0.8 — Market State Engine Coordinator

Primary coordinator integrating Volatility, Liquidity, Structure, Quality,
and Classification engines. Consumes normalized market data from Step 7.0
and persists market state snapshots into SQLite storage.
"""

from __future__ import annotations

import datetime
import sqlite3
from typing import Sequence

from goat.marketdata.core.enums import SafetyGateStatus
from goat.marketdata.core.models import MarketCandle, MarketGap, MarketStreamState, MarketTick
from goat.marketstate.classification.engine import MarketClassificationEngine
from goat.marketstate.core.canonical import compute_report_id
from goat.marketstate.core.models import (
    LiquidityAssessment,
    MarketQualityAssessment,
    MarketState,
    StructureAssessment,
    VolatilityAssessment,
)
from goat.marketstate.liquidity.engine import LiquidityAssessmentEngine
from goat.marketstate.persistence.repository import (
    LiquidityRepository,
    MarketStateReportRepository,
    MarketStateRepository,
    QualityRepository,
    StructureRepository,
    VolatilityRepository,
)
from goat.marketstate.quality.engine import MarketQualityEngine
from goat.marketstate.reporting.reports import (
    MarketStateExecutiveReport,
    MarketStateReport,
)
from goat.marketstate.structure.engine import StructureAssessmentEngine
from goat.marketstate.volatility.engine import VolatilityAssessmentEngine


class MarketStateEngine:
    """Primary coordinator for Market State Intelligence."""

    def __init__(self, db_conn: sqlite3.Connection | None = None):
        self.db_conn = db_conn

        self.volatility_engine = VolatilityAssessmentEngine()
        self.liquidity_engine = LiquidityAssessmentEngine()
        self.structure_engine = StructureAssessmentEngine()
        self.quality_engine = MarketQualityEngine()
        self.classification_engine = MarketClassificationEngine()

        if db_conn:
            self.volatility_repo = VolatilityRepository(db_conn)
            self.liquidity_repo = LiquidityRepository(db_conn)
            self.structure_repo = StructureRepository(db_conn)
            self.quality_repo = QualityRepository(db_conn)
            self.state_repo = MarketStateRepository(db_conn)
            self.report_repo = MarketStateReportRepository(db_conn)
        else:
            self.volatility_repo = None
            self.liquidity_repo = None
            self.structure_repo = None
            self.quality_repo = None
            self.state_repo = None
            self.report_repo = None

        self._active_states: dict[str, MarketState] = {}

    def evaluate_market_state(
        self,
        symbol: str,
        ticks: Sequence[MarketTick] = (),
        candles: Sequence[MarketCandle] = (),
        stream_state: MarketStreamState | None = None,
        gaps: Sequence[MarketGap] = (),
        safety_status: SafetyGateStatus = SafetyGateStatus.HEALTHY,
        replay_passed: bool = True,
        timestamp: str | None = None,
    ) -> MarketState:
        """Evaluate and synthesize full MarketState for a symbol."""
        sym = symbol.strip().upper()
        ts = timestamp if timestamp else datetime.datetime.now(datetime.timezone.utc).isoformat()

        # 1. Volatility Assessment
        if candles:
            vol_eval = self.volatility_engine.evaluate_candles(sym, candles)
        else:
            vol_eval = self.volatility_engine.evaluate_ticks(sym, ticks)

        # 2. Liquidity Assessment
        liq_eval = self.liquidity_engine.evaluate_ticks(sym, ticks)

        # 3. Structure Assessment
        if candles:
            struct_eval = self.structure_engine.evaluate_candles(sym, candles)
        else:
            struct_eval = self.structure_engine.evaluate_ticks(sym, ticks)

        # 4. Market Quality Assessment
        qual_eval = self.quality_engine.evaluate_quality(
            symbol=sym,
            stream_state=stream_state,
            recent_gaps=gaps,
            safety_status=safety_status,
            replay_integrity_passed=replay_passed,
        )

        # 5. Synthesize Market State
        market_state = self.classification_engine.classify(
            symbol=sym,
            volatility=vol_eval,
            liquidity=liq_eval,
            structure=struct_eval,
            quality=qual_eval,
            timestamp=ts,
        )

        # Store active state in memory
        self._active_states[sym] = market_state

        # Persist all components if database connection is available
        if self.db_conn:
            if self.volatility_repo:
                self.volatility_repo.save(vol_eval)
            if self.liquidity_repo:
                self.liquidity_repo.save(liq_eval)
            if self.structure_repo:
                self.structure_repo.save(struct_eval)
            if self.quality_repo:
                self.quality_repo.save(qual_eval)
            if self.state_repo:
                self.state_repo.save(market_state)

        return market_state

    def get_latest_market_state(self, symbol: str) -> MarketState | None:
        """Retrieve latest in-memory market state for a symbol."""
        return self._active_states.get(symbol.strip().upper())

    def generate_executive_report(self) -> MarketStateExecutiveReport:
        """Generate consolidated executive report summarizing all active market states."""
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        states_list = sorted(list(self._active_states.values()), key=lambda s: s.symbol)

        exec_id, canonical_hash = compute_report_id("EXECUTIVE", now_iso)
        exec_report = MarketStateExecutiveReport(
            report_id=exec_id,
            active_symbols_count=len(states_list),
            states=states_list,
            timestamp=now_iso,
            canonical_hash=canonical_hash,
        )

        if self.report_repo:
            self.report_repo.save_report(
                report_id=exec_id,
                report_type="EXECUTIVE",
                symbol="ALL",
                timestamp=now_iso,
                markdown_content=exec_report.to_markdown(),
                json_content=exec_report.to_json(),
                canonical_hash=canonical_hash,
            )

        return exec_report
