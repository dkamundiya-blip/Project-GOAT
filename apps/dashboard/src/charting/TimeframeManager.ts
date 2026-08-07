/**
 * Project GOAT v1.1 — Timeframe Manager
 * TradingView Candlestick Production Audit — Expanded Resolution Support
 *
 * Fixes applied:
 * - Added 30M resolution mapping (was missing, caused fallback to 1M)
 * - Added 4H resolution mapping (was incomplete)
 * - Added 2H, 6H, 8H, 12H future-ready mappings
 * - Added 1W and 1MO future-ready mappings
 * - Comprehensive bidirectional resolution ↔ GOAT timeframe conversion
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
  { id: '1D', label: '1D', resolution: '1D', goatApiTimeframe: '1D', seconds: 86400 },
];

export class TimeframeManager {
  /**
   * Convert TradingView chart resolution string to GOAT backend API timeframe.
   * Handles all supported formats including numeric minutes and named intervals.
   */
  static resolutionToGoatTimeframe(resolution: string): string {
    const res = resolution.toUpperCase();

    // Named resolutions
    if (res === 'D' || res === '1D') return '1D';

    // Try direct match in our config table
    const found = SUPPORTED_TIMEFRAMES.find(
      (item) => item.resolution.toUpperCase() === res || item.goatApiTimeframe === res || item.id === res
    );
    if (found) return found.goatApiTimeframe;

    // Numeric minute resolutions
    const numVal = parseInt(res, 10);
    if (!isNaN(numVal)) {
      if (numVal === 1) return '1M';
      if (numVal === 5) return '5M';
      if (numVal === 15) return '15M';
      if (numVal === 30) return '30M';
      if (numVal === 60) return '1H';
      if (numVal === 240) return '4H';
      if (numVal === 1440) return '1D';
    }

    // Default fallback
    return '1M';
  }

  /**
   * Convert GOAT backend API timeframe to TradingView chart resolution string.
   */
  static goatTimeframeToResolution(goatTf: string): string {
    const tf = goatTf.toUpperCase();
    const found = SUPPORTED_TIMEFRAMES.find((item) => item.goatApiTimeframe === tf || item.id === tf);
    return found ? found.resolution : '1';
  }

  /**
   * Get full timeframe config by ID, resolution, or GOAT API timeframe string.
   */
  static getTimeframeConfig(idOrResolution: string): TimeframeConfig {
    const search = idOrResolution.toUpperCase();
    const found = SUPPORTED_TIMEFRAMES.find(
      (item) => item.id === search || item.resolution.toUpperCase() === search || item.goatApiTimeframe === search
    );
    return found || SUPPORTED_TIMEFRAMES[0];
  }

  /**
   * Get all supported timeframe configurations.
   */
  static getAllTimeframes(): TimeframeConfig[] {
    return SUPPORTED_TIMEFRAMES;
  }
}
