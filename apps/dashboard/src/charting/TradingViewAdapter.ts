/**
 * Project GOAT v1.0 — TradingView Event & Stream Adapter
 * Step 1.6 Institutional TradingView Charting Engine
 */

import { ChartEvents } from './ChartEvents';
import { ChartPersistence } from './ChartPersistence';
import { SymbolManager } from './SymbolManager';
import { TimeframeManager } from './TimeframeManager';

export class TradingViewAdapter {
  static initializeAdapter(): void {
    // Listen to symbol changes and persist
    ChartEvents.on('SYMBOL_CHANGED', (payload) => {
      const state = ChartPersistence.loadState() || {
        symbol: 'VOLATILITY_100',
        timeframe: '1M',
        chartStyle: 'candlestick',
        layoutMode: 'single',
        theme: 'dark',
      };
      state.symbol = payload.data.symbol;
      ChartPersistence.saveState(state);
    });

    // Listen to timeframe changes and persist
    ChartEvents.on('TIMEFRAME_CHANGED', (payload) => {
      const state = ChartPersistence.loadState() || {
        symbol: 'VOLATILITY_100',
        timeframe: '1M',
        chartStyle: 'candlestick',
        layoutMode: 'single',
        theme: 'dark',
      };
      state.timeframe = payload.data.timeframe;
      ChartPersistence.saveState(state);
    });
  }

  static formatPriceForDisplay(price: number, symbolId: string): string {
    return SymbolManager.formatPrice(price, symbolId);
  }

  static getTimeframeLabel(timeframeId: string): string {
    return TimeframeManager.getTimeframeConfig(timeframeId).label;
  }
}
