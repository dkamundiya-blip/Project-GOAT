/**
 * Project GOAT v1.1 — Production TradingView DataFeed API Implementation
 * TradingView Candlestick Production Audit — Complete Rewrite
 *
 * ARCHITECTURAL RULES:
 * 1. TradingView DataFeed MUST NEVER communicate directly with Deriv.
 * 2. It consumes market data EXCLUSIVELY from GOAT Market Data REST API & WebSocket.
 * 3. Zero Math.random() or generated fallback data.
 * 4. Single WebSocket connection shared across all subscribers.
 * 5. Proper OHLC bar construction in DataFeed layer (not React state).
 * 6. Correct getBars() pagination with from/to range filtering.
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

type OnReadyCallback = (configurationData: object) => void;
type SearchSymbolsCallback = (items: object[]) => void;
type ResolveSymbolCallback = (symbolInfo: LibrarySymbolInfo) => void;
type HistoryCallback = (bars: BarData[], meta: { noData: boolean; nextTime?: number }) => void;
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
  BOOM500: 'BOOM_500',
  CRASH1000: 'CRASH_1000',
  CRASH500: 'CRASH_500',
  stpRNG: 'STEP_INDEX',
  STEP: 'STEP_INDEX',
  JUMP10: 'JUMP_10',
  JUMP25: 'JUMP_25',
  JUMP50: 'JUMP_50',
  JUMP75: 'JUMP_75',
  JUMP100: 'JUMP_100',
  JD10: 'JUMP_10',
  JD25: 'JUMP_25',
  JD50: 'JUMP_50',
  JD75: 'JUMP_75',
  JD100: 'JUMP_100',
};

function normalizeSymbol(sym: string): string {
  if (!sym) return '';
  const upper = sym.toUpperCase();
  return DERIV_TO_GOAT_SYMBOL_MAP[upper] || DERIV_TO_GOAT_SYMBOL_MAP[sym] || upper;
}

function getIntervalSeconds(goatTf: string): number {
  const cfg = TimeframeManager.getTimeframeConfig(goatTf);
  return cfg ? cfg.seconds : 60;
}

/**
 * Subscriber tracking for realtime bar updates.
 */
interface SubscriberEntry {
  symbol: string;
  resolution: string;
  goatTimeframe: string;
  intervalSeconds: number;
  callback: RealtimeCallback;
  resetCacheCallback: () => void;
  /** Last bar dispatched to this subscriber for OHLC aggregation */
  lastBar: BarData | null;
}

/**
 * Singleton TradingView DataFeed.
 * One instance shared across all chart panels.
 */
export class TradingViewDataFeed {
  private static _instance: TradingViewDataFeed | null = null;

  private subscribers: Map<string, SubscriberEntry> = new Map();
  private ws: WebSocket | null = null;
  private wsConnected: boolean = false;
  private pollingTimerId: ReturnType<typeof setInterval> | null = null;
  private pollFallbackActive: boolean = false;
  private _destroyed: boolean = false;

  /**
   * Returns the singleton DataFeed instance.
   */
  static getInstance(): TradingViewDataFeed {
    if (!TradingViewDataFeed._instance || TradingViewDataFeed._instance._destroyed) {
      TradingViewDataFeed._instance = new TradingViewDataFeed();
    }
    return TradingViewDataFeed._instance;
  }

  private constructor() {
    console.log('[TradingViewDataFeed] Singleton DataFeed initialized.');
  }

  /**
   * Destroy the DataFeed instance, cleaning up all connections and timers.
   */
  destroy(): void {
    this._destroyed = true;
    this.subscribers.clear();

    if (this.pollingTimerId !== null) {
      clearInterval(this.pollingTimerId);
      this.pollingTimerId = null;
    }

    if (this.ws) {
      try {
        this.ws.close();
      } catch {
        // Ignore close errors
      }
      this.ws = null;
    }

    this.wsConnected = false;
    TradingViewDataFeed._instance = null;
    console.log('[TradingViewDataFeed] DataFeed destroyed.');
  }

  // =====================================================================
  // 1. onReady — Returns DataFeed capabilities
  // =====================================================================
  onReady(callback: OnReadyCallback): void {
    console.log('[TradingViewDataFeed] onReady called');
    setTimeout(() => {
      callback({
        supports_search: true,
        supports_group_request: false,
        supports_marks: true,
        supports_timescale_marks: true,
        supports_time: true,
        supported_resolutions: ['1', '5', '15', '30', '60', '240', '1D'],
      });
    }, 0);
  }

  // =====================================================================
  // 2. searchSymbols — Searches supported GOAT synthetic instruments
  // =====================================================================
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

  // =====================================================================
  // 3. resolveSymbol — Resolves symbol metadata with correct precision
  // =====================================================================
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

  // =====================================================================
  // 4. getBars — Fetches historical OHLCV bars with proper pagination
  // =====================================================================
  async getBars(
    symbolInfo: LibrarySymbolInfo,
    resolution: string,
    periodParams: { from: number; to: number; firstDataRequest: boolean; countBack?: number },
    onHistoryCallback: HistoryCallback,
    _onErrorCallback: ErrorCallback
  ): Promise<void> {
    const symbolId = symbolInfo.name;
    const goatTf = TimeframeManager.resolutionToGoatTimeframe(resolution);

    // Request limit: use countBack if available, otherwise default to 300
    const limit = periodParams.countBack || 300;
    const url = `/api/v1/market-data/candles/history/${symbolId}?timeframe=${goatTf}&limit=${limit}`;

    console.log('[TradingViewDataFeed] getBars:', { symbol: symbolId, resolution, goatTf, from: periodParams.from, to: periodParams.to, limit });

    try {
      const res = await fetch(url);
      if (!res.ok) {
        console.warn('[TradingViewDataFeed] getBars HTTP error:', res.status, res.statusText);
        onHistoryCallback([], { noData: true });
        return;
      }
      const json = await res.json();
      const rawCandles = json.data?.candles || json.candles || [];

      if (rawCandles.length === 0) {
        onHistoryCallback([], { noData: true });
        return;
      }

      // Convert backend candle format to BarData
      const allBars: BarData[] = rawCandles.map((c: Record<string, unknown>) => ({
        time: new Date(c.open_timestamp as string).getTime(),
        open: Number(c.open),
        high: Number(c.high),
        low: Number(c.low),
        close: Number(c.close),
        volume: Number(c.volume || 0),
      }));

      // Sort ascending by time (critical for TradingView)
      allBars.sort((a, b) => a.time - b.time);

      // Deduplicate by timestamp
      const seen = new Set<number>();
      const dedupedBars: BarData[] = [];
      for (const bar of allBars) {
        if (!seen.has(bar.time)) {
          seen.add(bar.time);
          dedupedBars.push(bar);
        }
      }

      // Validate OHLC integrity — skip impossible candles
      const validBars = dedupedBars.filter((bar) => {
        if (bar.high < bar.low) return false;
        if (bar.open > bar.high || bar.open < bar.low) return false;
        if (bar.close > bar.high || bar.close < bar.low) return false;
        if (bar.open <= 0 || bar.high <= 0 || bar.low <= 0 || bar.close <= 0) return false;
        return true;
      });

      // Filter by requested time range (from/to are in seconds, bar.time is in ms)
      const fromMs = periodParams.from * 1000;
      const toMs = periodParams.to * 1000;
      const filteredBars = validBars.filter((bar) => bar.time >= fromMs && bar.time <= toMs);

      // If no bars in range, signal noData with nextTime hint for scrollback
      if (filteredBars.length === 0) {
        if (validBars.length > 0) {
          // Give TradingView a hint about where earlier data exists
          const earliestBar = validBars[0];
          onHistoryCallback([], { noData: true, nextTime: Math.floor(earliestBar.time / 1000) });
        } else {
          onHistoryCallback([], { noData: true });
        }
        return;
      }

      // Seed matching active subscribers' lastBar with the latest historical bar
      if (validBars.length > 0) {
        const latestHistBar = validBars[validBars.length - 1];
        const normSym = normalizeSymbol(symbolId);
        for (const [, sub] of this.subscribers.entries()) {
          if (normalizeSymbol(sub.symbol) === normSym && sub.resolution === resolution) {
            if (!sub.lastBar || latestHistBar.time >= sub.lastBar.time) {
              sub.lastBar = { ...latestHistBar };
            }
          }
        }
      }

      console.log('[TradingViewDataFeed] getBars returning:', filteredBars.length, 'bars');
      onHistoryCallback(filteredBars, { noData: false });
    } catch (err) {
      console.error('[TradingViewDataFeed] getBars fetch exception:', err);
      onHistoryCallback([], { noData: true });
    }
  }

  // =====================================================================
  // 5. subscribeBars — Subscribes to realtime updates with proper OHLC
  // =====================================================================
  subscribeBars(
    symbolInfo: LibrarySymbolInfo,
    resolution: string,
    onRealtimeCallback: RealtimeCallback,
    subscriberUID: string,
    onResetCacheNeededCallback: () => void
  ): void {
    const goatTf = TimeframeManager.resolutionToGoatTimeframe(resolution);
    const intervalSec = getIntervalSeconds(goatTf);

    console.log('[TradingViewDataFeed] subscribeBars:', { subscriberUID, symbol: symbolInfo.name, resolution, goatTf });

    this.subscribers.set(subscriberUID, {
      symbol: symbolInfo.name,
      resolution: resolution,
      goatTimeframe: goatTf,
      intervalSeconds: intervalSec,
      callback: onRealtimeCallback,
      resetCacheCallback: onResetCacheNeededCallback,
      lastBar: null,
    });

    // Ensure realtime connection is active when we have subscribers
    this.ensureRealtimeConnection();
  }

  // =====================================================================
  // 6. unsubscribeBars — Unsubscribes from realtime updates
  // =====================================================================
  unsubscribeBars(subscriberUID: string): void {
    console.log('[TradingViewDataFeed] unsubscribeBars:', subscriberUID);
    this.subscribers.delete(subscriberUID);

    // If no subscribers remain, we can stop polling (WS stays for reconnect)
    if (this.subscribers.size === 0 && this.pollingTimerId !== null) {
      clearInterval(this.pollingTimerId);
      this.pollingTimerId = null;
      this.pollFallbackActive = false;
    }
  }

  // =====================================================================
  // 7. calculateHistoryDepth — Backward compatibility (deprecated in v2)
  // =====================================================================
  calculateHistoryDepth(resolution: string, _resolutionBack: string, _intervalBack: number): { resolutionBack: string; intervalBack: number } | undefined {
    if (resolution === '1' || resolution === '5') {
      return { resolutionBack: 'D', intervalBack: 3 };
    }
    return { resolutionBack: 'M', intervalBack: 1 };
  }

  // =====================================================================
  // 8. getMarks — Returns research marks
  // =====================================================================
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

  // =====================================================================
  // 9. getTimescaleMarks — Returns timescale marks
  // =====================================================================
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

  // =====================================================================
  // 10. getServerTime — Returns UTC server timestamp
  // =====================================================================
  getServerTime(callback: GetServerTimeCallback): void {
    setTimeout(() => {
      callback(Math.floor(Date.now() / 1000));
    }, 0);
  }

  // =====================================================================
  // PRIVATE: Realtime Connection Management
  // =====================================================================

  /**
   * Ensure exactly one realtime connection is active.
   * Primary: WebSocket. Fallback: HTTP polling (only if WS fails).
   */
  private ensureRealtimeConnection(): void {
    if (this._destroyed) return;

    // Try WebSocket first
    if (!this.ws || this.ws.readyState === WebSocket.CLOSED || this.ws.readyState === WebSocket.CLOSING) {
      this.initWebSocket();
    }
  }

  /**
   * Initialize single WebSocket connection to backend gateway.
   */
  private initWebSocket(): void {
    if (this._destroyed || typeof window === 'undefined') return;

    try {
      // Environment-Aware WebSocket URL Resolution
      let wsUrl: string;
      const envWsUrl = (import.meta as any).env?.VITE_MARKET_WS_URL;

      if (envWsUrl) {
        wsUrl = envWsUrl;
      } else if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        wsUrl = `${protocol}//${window.location.host}/api/v1/market-data/ws`;
      } else {
        wsUrl = 'wss://project-goat-production.up.railway.app/api/v1/market-data/ws';
      }

      console.log('[TradingViewDataFeed] Connecting WebSocket:', wsUrl);
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('[TradingViewDataFeed] WebSocket connected');
        this.wsConnected = true;

        // Stop HTTP polling fallback if WS is now connected
        if (this.pollingTimerId !== null) {
          clearInterval(this.pollingTimerId);
          this.pollingTimerId = null;
          this.pollFallbackActive = false;
          console.log('[TradingViewDataFeed] Stopped HTTP polling fallback (WS active)');
        }
      };

      this.ws.onerror = () => {
        console.warn('[TradingViewDataFeed] WebSocket error');
        this.wsConnected = false;
        this.startPollingFallback();
      };

      this.ws.onclose = () => {
        console.log('[TradingViewDataFeed] WebSocket closed');
        this.wsConnected = false;
        // Start polling fallback if we still have subscribers
        if (this.subscribers.size > 0 && !this._destroyed) {
          this.startPollingFallback();
        }
      };

      this.ws.onmessage = (event) => {
        this.handleWebSocketMessage(event);
      };
    } catch (err) {
      console.warn('[TradingViewDataFeed] WebSocket init exception:', err);
      this.wsConnected = false;
      this.startPollingFallback();
    }
  }

  /**
   * Process WebSocket tick message and build proper OHLC bars.
   */
  private handleWebSocketMessage(event: MessageEvent): void {
    try {
      const payload = JSON.parse(event.data);
      const rawTick = payload.tick || payload;
      const rawSymbol = rawTick.symbol;
      const price = Number(rawTick.price || rawTick.quote);
      const epochSec = rawTick.epoch ? Number(rawTick.epoch) : Math.floor(Date.now() / 1000);

      if (!rawSymbol || isNaN(price) || price <= 0) return;

      const normalizedSym = normalizeSymbol(rawSymbol);

      // Dispatch to matching subscribers with proper OHLC construction
      for (const [, sub] of this.subscribers.entries()) {
        const subSymNormalized = normalizeSymbol(sub.symbol);
        if (subSymNormalized !== normalizedSym) continue;

        // Floor tick time to interval boundary
        const barTimeMs = Math.floor(epochSec / sub.intervalSeconds) * sub.intervalSeconds * 1000;

        const lastBar = sub.lastBar;

        if (lastBar && lastBar.time === barTimeMs) {
          // Same interval — update forming candle
          const updatedBar: BarData = {
            time: barTimeMs,
            open: lastBar.open,
            high: Math.max(lastBar.high, price),
            low: Math.min(lastBar.low, price),
            close: price,
            volume: lastBar.volume + 1,
          };
          sub.lastBar = updatedBar;
          sub.callback(updatedBar);
        } else if (!lastBar || barTimeMs > lastBar.time) {
          // New interval — create new bar
          const newBar: BarData = {
            time: barTimeMs,
            open: price,
            high: price,
            low: price,
            close: price,
            volume: 1,
          };
          sub.lastBar = newBar;
          sub.callback(newBar);
        }
        // Ignore ticks with barTimeMs < lastBar.time (stale/out-of-order)
      }
    } catch {
      // Non-JSON or malformed frame — silently ignore
    }
  }

  /**
   * HTTP polling fallback — only activated when WebSocket is unavailable.
   */
  private startPollingFallback(): void {
    if (this._destroyed || this.pollFallbackActive) return;
    this.pollFallbackActive = true;

    console.log('[TradingViewDataFeed] Starting HTTP polling fallback');
    this.pollingTimerId = setInterval(async () => {
      if (this.subscribers.size === 0 || this.wsConnected) return;

      for (const [, sub] of this.subscribers.entries()) {
        try {
          const url = `/api/v1/market-data/candles/latest/${sub.symbol}?timeframe=${sub.goatTimeframe}`;
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
                volume: Number(c.volume || 0),
              };
              // Only dispatch if bar is valid
              if (bar.open > 0 && bar.high >= bar.low && bar.close > 0) {
                sub.lastBar = bar;
                sub.callback(bar);
              }
            }
          }
        } catch {
          // Ignore offline polling errors
        }
      }
    }, 2000);
  }
}
