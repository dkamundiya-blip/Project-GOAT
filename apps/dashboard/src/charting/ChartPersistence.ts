/**
 * Project GOAT v1.0 — Chart State Persistence
 * Step 1.6 Institutional TradingView Charting Engine
 */

export interface PersistedChartState {
  symbol: string;
  timeframe: string;
  chartStyle: string;
  layoutMode: string;
  theme: string;
}

const STORAGE_KEY = 'GOAT_TRADINGVIEW_CHART_PREFERENCES';

export class ChartPersistence {
  static saveState(state: PersistedChartState): void {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch {
      // Ignore local storage save error
    }
  }

  static loadState(): PersistedChartState | null {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) {
        return JSON.parse(raw);
      }
    } catch {
      // Ignore local storage read error
    }
    return null;
  }
}
