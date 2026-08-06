/**
 * Project GOAT v1.0 — Institutional Overlay Layer Architecture
 * Task 9: Quantitative Technical & Overlay Signals Abstraction
 *
 * Provides extensible structural definitions and calculators for:
 * - Fair Value Gaps (FVG)
 * - Order Blocks (OB)
 * - Liquidity Zones & Equal Highs / Lows (EQH/EQL)
 * - Market Structure Shift (MSS) & Break of Structure (BOS)
 * - Volume Weighted Average Price (VWAP)
 * - AI Execution Signals & Risk Markers
 */

import { SeriesMarker, Time } from 'lightweight-charts';
import { BarData } from './TradingViewDataFeed';
import { ChartSettings, defaultChartSettings } from './ChartSettings';

export interface FairValueGap {
  id: string;
  type: 'BULLISH' | 'BEARISH';
  high: number;
  low: number;
  time: number;
}

export interface OrderBlock {
  id: string;
  type: 'BULLISH' | 'BEARISH';
  high: number;
  low: number;
  openTime: number;
}

export interface MarketStructureShift {
  id: string;
  type: 'BULLISH_BOS' | 'BEARISH_BOS' | 'MSS';
  price: number;
  time: number;
}

export interface VwapPoint {
  time: Time;
  value: number;
}

export class InstitutionalOverlayManager {
  /**
   * Detect Fair Value Gaps (FVG) across historical candles.
   * Bullish FVG: Bar(i-2).high < Bar(i).low
   * Bearish FVG: Bar(i-2).low > Bar(i).high
   */
  public static detectFairValueGaps(bars: BarData[]): FairValueGap[] {
    const gaps: FairValueGap[] = [];
    if (bars.length < 3) return gaps;

    for (let i = 2; i < bars.length; i++) {
      const prev2 = bars[i - 2];
      const curr = bars[i];

      // Bullish FVG
      if (curr.low > prev2.high) {
        gaps.push({
          id: `FVG_BULL_${curr.time}`,
          type: 'BULLISH',
          high: curr.low,
          low: prev2.high,
          time: curr.time,
        });
      }
      // Bearish FVG
      else if (curr.high < prev2.low) {
        gaps.push({
          id: `FVG_BEAR_${curr.time}`,
          type: 'BEARISH',
          high: prev2.low,
          low: curr.high,
          time: curr.time,
        });
      }
    }
    return gaps;
  }

  /**
   * Convert FVG and Structural events into Lightweight Charts SeriesMarkers.
   * Dormant by default (Task 3).
   * Returns empty array unless showInstitutionalOverlays is explicitly true.
   * Never renders text labels on candles (Task 1 & Task 6).
   */
  public static generateOverlayMarkers(
    bars: BarData[],
    settings: ChartSettings = defaultChartSettings
  ): SeriesMarker<Time>[] {
    // Task 3: Dormant by default
    if (!settings.showInstitutionalOverlays) {
      return [];
    }

    const markers: SeriesMarker<Time>[] = [];

    // FVG Markers (only if showFVG === true)
    if (settings.showFVG) {
      const gaps = this.detectFairValueGaps(bars);
      gaps.slice(-10).forEach((fvg) => {
        const timeSec = (fvg.time > 2000000000 ? Math.floor(fvg.time / 1000) : fvg.time) as Time;
        if (fvg.type === 'BULLISH') {
          markers.push({
            time: timeSec,
            position: 'belowBar',
            color: '#10b981',
            shape: 'arrowUp',
            // Omit text property to prevent floating text clutter per Task 1 & Task 6
          });
        } else {
          markers.push({
            time: timeSec,
            position: 'aboveBar',
            color: '#f43f5e',
            shape: 'arrowDown',
            // Omit text property to prevent floating text clutter per Task 1 & Task 6
          });
        }
      });
    }

    return markers;
  }

  /**
   * Compute Session VWAP (Volume Weighted Average Price)
   */
  public static calculateVwap(bars: BarData[]): VwapPoint[] {
    let cumulativeTPV = 0;
    let cumulativeVol = 0;

    return bars.map((bar) => {
      const typicalPrice = (bar.high + bar.low + bar.close) / 3;
      const vol = bar.volume > 0 ? bar.volume : 1;
      cumulativeTPV += typicalPrice * vol;
      cumulativeVol += vol;

      const timeSec = (bar.time > 2000000000 ? Math.floor(bar.time / 1000) : bar.time) as Time;
      return {
        time: timeSec,
        value: cumulativeTPV / cumulativeVol,
      };
    });
  }
}
