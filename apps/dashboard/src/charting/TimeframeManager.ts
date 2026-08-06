/**
 * Project GOAT v1.0 — Timeframe Manager
 * Step 1.6 Institutional TradingView Charting Engine
 */

export interface TimeframeConfig {
  id: string;
  label: string;
  resolution: string; // TradingView resolution string ('1', '5', '15', '30', '60', '240', 'D')
  goatApiTimeframe: string; // GOAT backend timeframe string ('1M', '5M', '15M', '30M', '1H', '4H', '1D')
  seconds: number;
}

export const SUPPORTED_TIMEFRAMES: TimeframeConfig[] = [
  { id: '1M', label: '1m', resolution: '1', goatApiTimeframe: '1M', seconds: 60 },
  { id: '5M', label: '5m', resolution: '5', goatApiTimeframe: '5M', seconds: 300 },
  { id: '15M', label: '15m', resolution: '15', goatApiTimeframe: '15M', seconds: 900 },
  { id: '30M', label: '30m', resolution: '30', goatApiTimeframe: '30M', seconds: 1800 },
  { id: '1H', label: '1h', resolution: '60', goatApiTimeframe: '1H', seconds: 3600 },
  { id: '4H', label: '4h', resolution: '240', goatApiTimeframe: '4H', seconds: 14400 },
  { id: '1D', label: '1d', resolution: 'D', goatApiTimeframe: '1D', seconds: 86400 },
];

export class TimeframeManager {
  static resolutionToGoatTimeframe(resolution: string): string {
    const res = resolution.toUpperCase();
    if (res === 'D' || res === '1D') return '1D';
    if (res === '240' || res === '4H') return '4H';
    if (res === '60' || res === '1H') return '1H';
    if (res === '30' || res === '30M') return '30M';
    if (res === '15' || res === '15M') return '15M';
    if (res === '5' || res === '5M') return '5M';
    return '1M';
  }

  static goatTimeframeToResolution(goatTf: string): string {
    const tf = goatTf.toUpperCase();
    const found = SUPPORTED_TIMEFRAMES.find((item) => item.goatApiTimeframe === tf);
    return found ? found.resolution : '1';
  }

  static getTimeframeConfig(idOrResolution: string): TimeframeConfig {
    const search = idOrResolution.toUpperCase();
    const found = SUPPORTED_TIMEFRAMES.find(
      (item) => item.id === search || item.resolution === search || item.goatApiTimeframe === search
    );
    return found || SUPPORTED_TIMEFRAMES[0];
  }

  static getAllTimeframes(): TimeframeConfig[] {
    return SUPPORTED_TIMEFRAMES;
  }
}
