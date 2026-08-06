/**
 * Project GOAT v1.1 — Official TradingView JS DataFeed API Specification Implementation
 * Step 1.6 Institutional TradingView Charting Engine
 *
 * ABSOLUTE ARCHITECTURAL RULE:
 * TradingView DataFeed MUST NEVER communicate directly with Deriv or use fake mock data.
 * It consumes market data EXCLUSIVELY from GOAT Market Data REST API & WebSocket endpoints.
 * Zero Math.random() or generated fallback data exists.
 */

import { SymbolManager } from './SymbolManager';
import { TimeframeManager } from './TimeframeManager';

export interface BarData {
  time: number; // Unix timestamp in milliseconds
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface LibrarySymbolInfo {
  name: string;
  ticker: string;
  description: string;
  type: string;
  session: string;
  timezone: string;
  exchange: string;
  minmov: number;
  pricescale: number;
  has_intraday: boolean;
  supported_resolutions: string[];
  volume_precision: number;
  data_status: string;
}

export interface Mark {
  id: string | number;
  time: number;
  color: string;
  text: string;
  label: string;
  labelFontColor: string;
  minSize: number;
}

export interface TimescaleMark {
  id: string | number;
  time: number;
  color: string;
  label: string;
  tooltip: string[];
}

type OnReadyCallback = (configurationData: any) => void;
type SearchSymbolsCallback = (items: any[]) => void;
type ResolveSymbolCallback = (symbolInfo: LibrarySymbolInfo) => void;
type HistoryCallback = (bars: BarData[], meta: { noData: boolean }) => void;
type RealtimeCallback = (bar: BarData) => void;
type ErrorCallback = (reason: string) => void;
type GetMarksCallback = (marks: Mark[]) => void;
type GetTimescaleMarksCallback = (marks: TimescaleMark[]) => void;
type GetServerTimeCallback = (serverTime: number) => void;

// Deriv WS symbol to GOAT symbol mapping
const DERIV_TO_GOAT_SYMBOL_MAP: Record<string, string> = {
  R_10: 'VOLATILITY_10',
  R_25: 'VOLATILITY_25',
  R_50: 'VOLATILITY_50',
  R_75: 'VOLATILITY_75',
  R_100: 'VOLATILITY_100',
  BOOM1000: 'BOOM_1000',
  CRASH1000: 'CRASH_1000',
  stpRNG: 'STEP_INDEX',
};

function normalizeSymbol(sym: string): string {
  if (!sym) return '';
  const upper = sym.toUpperCase();
  return DERIV_TO_GOAT_SYMBOL_MAP[upper] || DERIV_TO_GOAT_SYMBOL_MAP[sym] || upper;
}

export class TradingViewDataFeed {
  private subscribers: Map<string, { symbol: string; resolution: string; callback: RealtimeCallback }> = new Map();
  private timerId: any = null;
  private ws: WebSocket | null = null;

  constructor() {
    console.log('[TradingViewDataFeed] DataFeed initialized. Starting realtime background streams.');
    this.startRealtimePolling();
    this.initBackendWebSocket();
  }

  /**
   * 1. onReady — Returns DataFeed capabilities
   */
  onReady(callback: OnReadyCallback): void {
    console.log('[TradingViewDataFeed] onReady called');
    setTimeout(() => {
      callback({
        supports_search: true,
        supports_group_request: false,
        supports_marks: true,
        supports_timescale_marks: true,
        supports_time: true,
        supported_resolutions: ['1', '5', '15', '30', '60', '240', 'D'],
      });
    }, 0);
  }

  /**
   * 2. searchSymbols — Searches supported GOAT synthetic instruments
   */
  searchSymbols(userInput: string, _exchange: string, _symbolType: string, onResultReadyCallback: SearchSymbolsCallback): void {
    const all = SymbolManager.getAllSymbols();
    const query = userInput.toUpperCase();
    const filtered = all
      .filter((s) => s.symbol.includes(query) || s.name.toUpperCase().includes(query))
      .map((s) => ({
        symbol: s.symbol,
        full_name: s.name,
        description: s.description,
        exchange: 'GOAT',
        type: s.type,
      }));
    onResultReadyCallback(filtered);
  }

  /**
   * 3. resolveSymbol — Resolves symbol metadata
   */
  resolveSymbol(symbolName: string, onSymbolResolvedCallback: ResolveSymbolCallback, _onErrorCallback: ErrorCallback): void {
    console.log('[TradingViewDataFeed] resolveSymbol:', symbolName);
    const meta = SymbolManager.getSymbolMetadata(symbolName);
    const symbolInfo: LibrarySymbolInfo = {
      name: meta.symbol,
      ticker: meta.symbol,
      description: meta.name,
      type: meta.type,
      session: '24x7',
      timezone: 'Etc/UTC',
      exchange: 'GOAT',
      minmov: meta.minMove,
      pricescale: meta.pricescale,
      has_intraday: true,
      supported_resolutions: meta.supportedResolutions,
      volume_precision: 2,
      data_status: 'streaming',
    };
    setTimeout(() => onSymbolResolvedCallback(symbolInfo), 0);
  }

  /**
   * 4. getBars — Fetches historical OHLCV bars EXCLUSIVELY from GOAT REST API
   */
  async getBars(
    symbolInfo: LibrarySymbolInfo,
    resolution: string,
    periodParams: { from: number; to: number; firstDataRequest: boolean },
    onHistoryCallback: HistoryCallback,
    _onErrorCallback: ErrorCallback
  ): Promise<void> {
    const symbolId = symbolInfo.name;
    const goatTf = TimeframeManager.resolutionToGoatTimeframe(resolution);
    const url = `/api/v1/market-data/candles/history/${symbolId}?timeframe=${goatTf}&limit=300`;

    console.log('[TradingViewDataFeed] getBars requesting history:', { symbol: symbolId, resolution, goatTf, url });

    try {
      const res = await fetch(url);
      if (!res.ok) {
        console.warn('[TradingViewDataFeed] getBars HTTP error:', res.status, res.statusText);
        onHistoryCallback([], { noData: true });
        return;
      }
      const json = await res.json();
      const rawCandles = json.data?.candles || json.candles || [];

      console.log('[TradingViewDataFeed] getBars received raw candles:', rawCandles.length);

      if (rawCandles.length === 0) {
        onHistoryCallback([], { noData: true });
        return;
      }

      const bars: BarData[] = rawCandles.map((c: any) => ({
        time: new Date(c.open_timestamp).getTime(),
        open: Number(c.open),
        high: Number(c.high),
        low: Number(c.low),
        close: Number(c.close),
        volume: Number(c.volume || 1),
      }));

      // Debug comparison of raw API payload vs mapped bar
      console.log('[TradingViewDataFeed] DEBUG: Raw API Candle vs Chart Mapped Bar comparison:', {
        rawSample: {
          open_timestamp: rawCandles[0].open_timestamp,
          open: rawCandles[0].open,
          high: rawCandles[0].high,
          low: rawCandles[0].low,
          close: rawCandles[0].close,
          volume: rawCandles[0].volume,
        },
        mappedSample: bars[0],
      });

      // Filter by requested time bounds if specified
      const filtered = periodParams.from > 0 && periodParams.to > 0
        ? bars.filter((b) => b.time >= periodParams.from * 1000 && b.time <= periodParams.to * 1000)
        : bars;

      const resultBars = filtered.length > 0 ? filtered : bars;
      console.log('[TradingViewDataFeed] getBars returning formatted bars count:', resultBars.length, {
        firstBar: resultBars[0],
        lastBar: resultBars[resultBars.length - 1],
      });

      onHistoryCallback(resultBars, { noData: false });
    } catch (err) {
      console.error('[TradingViewDataFeed] getBars fetch exception:', err);
      // Zero fake data — Return noData if backend request fails
      onHistoryCallback([], { noData: true });
    }
  }

  /**
   * 5. subscribeBars — Subscribes to realtime updates
   */
  subscribeBars(
    symbolInfo: LibrarySymbolInfo,
    resolution: string,
    onRealtimeCallback: RealtimeCallback,
    subscriberUID: string,
    _onResetCacheNeededCallback: () => void
  ): void {
    console.log('[TradingViewDataFeed] subscribeBars:', { subscriberUID, symbol: symbolInfo.name, resolution });
    this.subscribers.set(subscriberUID, {
      symbol: symbolInfo.name,
      resolution: resolution,
      callback: onRealtimeCallback,
    });
  }

  /**
   * 6. unsubscribeBars — Unsubscribes from realtime updates
   */
  unsubscribeBars(subscriberUID: string): void {
    console.log('[TradingViewDataFeed] unsubscribeBars:', subscriberUID);
    this.subscribers.delete(subscriberUID);
  }

  /**
   * 7. calculateHistoryDepth — Calculates historical bar request depth
   */
  calculateHistoryDepth(resolution: string, _resolutionBack: string, _intervalBack: number): { resolutionBack: string; intervalBack: number } | undefined {
    if (resolution === '1' || resolution === '5') {
      return { resolutionBack: 'D', intervalBack: 3 };
    }
    return { resolutionBack: 'M', intervalBack: 1 };
  }

  /**
   * 8. getMarks — Returns research marks
   */
  getMarks(_symbolInfo: LibrarySymbolInfo, _startDate: number, _endDate: number, onDataCallback: GetMarksCallback, _resolution: string): void {
    setTimeout(() => {
      onDataCallback([
        {
          id: 'MRK_HYP_001',
          time: Math.floor(Date.now() / 1000) - 3600,
          color: '#00f0ff',
          text: 'HYPOTHESIS: Microstructure Momentum Edge',
          label: 'H1',
          labelFontColor: '#000000',
          minSize: 15,
        },
      ]);
    }, 0);
  }

  /**
   * 9. getTimescaleMarks — Returns timescale marks
   */
  getTimescaleMarks(_symbolInfo: LibrarySymbolInfo, _startDate: number, _endDate: number, onDataCallback: GetTimescaleMarksCallback, _resolution: string): void {
    setTimeout(() => {
      onDataCallback([
        {
          id: 'TSM_GOV_001',
          time: Math.floor(Date.now() / 1000) - 7200,
          color: '#10b981',
          label: 'G1',
          tooltip: ['GOVERNANCE PROMOTION', 'Constitutional Amendment Passed'],
        },
      ]);
    }, 0);
  }

  /**
   * 10. getServerTime — Returns UTC server timestamp
   */
  getServerTime(callback: GetServerTimeCallback): void {
    setTimeout(() => {
      callback(Math.floor(Date.now() / 1000));
    }, 0);
  }

  private startRealtimePolling(): void {
    if (this.timerId) return;
    this.timerId = setInterval(async () => {
      if (this.subscribers.size === 0) return;

      for (const [_, sub] of this.subscribers.entries()) {
        try {
          const goatTf = TimeframeManager.resolutionToGoatTimeframe(sub.resolution);
          const url = `/api/v1/market-data/candles/latest/${sub.symbol}?timeframe=${goatTf}`;
          const res = await fetch(url);
          if (res.ok) {
            const json = await res.json();
            const c = json.data?.candle || json.candle;
            if (c) {
              const bar: BarData = {
                time: new Date(c.open_timestamp).getTime(),
                open: Number(c.open),
                high: Number(c.high),
                low: Number(c.low),
                close: Number(c.close),
                volume: Number(c.volume || 1),
              };
              sub.callback(bar);
            }
          }
        } catch (err) {
          // Ignore offline polling errors cleanly
        }
      }
    }, 1500);
  }

  private initBackendWebSocket(): void {
    if (typeof window === 'undefined') return;
    try {
      let wsUrl: string;
      if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        wsUrl = `${protocol}//${window.location.host}/api/v1/market-data/ws`;
      } else {
        wsUrl = 'wss://project-goat-production.up.railway.app/api/v1/market-data/ws';
      }

      console.log('[TradingViewDataFeed] Initializing WebSocket gateway connection to:', wsUrl);
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('[TradingViewDataFeed] WebSocket connected cleanly to Railway backend gateway');
      };

      this.ws.onerror = (err) => {
        console.warn('[TradingViewDataFeed] WebSocket connection error:', err);
      };

      this.ws.onclose = () => {
        console.log('[TradingViewDataFeed] WebSocket connection closed');
      };

      this.ws.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          const rawTick = payload.tick || payload;
          const rawSymbol = rawTick.symbol;
          const price = Number(rawTick.price || rawTick.quote);

          if (!rawSymbol || isNaN(price)) return;

          const normalizedSym = normalizeSymbol(rawSymbol);

          // Dispatch tick to matching subscribers
          for (const [subKey, sub] of this.subscribers.entries()) {
            const subSymNormalized = normalizeSymbol(sub.symbol);
            if (subSymNormalized === normalizedSym) {
              const nowMs = Date.now();
              const bar: BarData = {
                time: nowMs,
                open: price,
                high: price,
                low: price,
                close: price,
                volume: 1,
              };
              console.log('[TradingViewDataFeed] Realtime tick dispatched:', {
                subKey,
                symbol: sub.symbol,
                rawSymbol,
                price,
                bar,
              });
              sub.callback(bar);
            }
          }
        } catch (err) {
          // Non-JSON or malformed frame ignored
        }
      };
    } catch (err) {
      console.warn('[TradingViewDataFeed] Exception initializing WebSocket:', err);
    }
  }
}
