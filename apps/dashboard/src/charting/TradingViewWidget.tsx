/**
 * Project GOAT v1.1 — Institutional TradingView Lightweight Charts Renderer
 * TradingView Candlestick Production Audit — Simplified Architecture
 *
 * Fixes applied:
 * - Uses shared DataFeed singleton (no per-panel DataFeed instances)
 * - Removes React-state OHLC aggregation (moved to DataFeed layer)
 * - Clean separation: initial historical load → streaming subscription
 * - Proper cleanup on unmount / symbol / timeframe change
 */

import React, { useRef, useEffect, useState, useCallback } from 'react';
import { SymbolManager } from './SymbolManager';
import { TimeframeManager } from './TimeframeManager';
import { TradingViewDataFeed, BarData, LibrarySymbolInfo } from './TradingViewDataFeed';
import { ChartStyleType, CrosshairModeType, ThemeType } from './ChartState';
import { DrawingToolType } from './DrawingManager';
import { ChartContainer } from './ChartContainer';
import { ChartSettings, defaultChartSettings } from './ChartSettings';
import { Position } from '../components/widgets/OrderTicketWidget';

export interface TradingViewWidgetProps {
  panelId?: string;
  symbol: string;
  timeframe: string;
  chartStyle?: ChartStyleType;
  crosshairMode?: CrosshairModeType;
  activeTool?: DrawingToolType;
  theme?: ThemeType;
  height?: number | string;
  showVolume?: boolean;
  showGridLines?: boolean;
  activePositions?: Position[];
  bidPrice?: number;
  askPrice?: number;
  lastPrice?: number;
  chartSettings?: ChartSettings;
  onCrosshairMove?: (price: number | null, time: number | null) => void;
}

export const TradingViewWidget: React.FC<TradingViewWidgetProps> = ({
  panelId = 'panel_primary',
  symbol,
  timeframe,
  theme = 'dark',
  height = '100%',
  activePositions = [],
  bidPrice,
  askPrice,
  lastPrice,
  chartSettings = defaultChartSettings,
  onCrosshairMove,
}) => {
  const [bars, setBars] = useState<BarData[]>([]);
  const barsRef = useRef<BarData[]>([]);
  const subscriberIdRef = useRef<string>('');

  // Build symbolInfo from metadata — memoized by symbol
  const buildSymbolInfo = useCallback((sym: string): LibrarySymbolInfo => {
    const meta = SymbolManager.getSymbolMetadata(sym);
    return {
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
  }, []);

  // Load historical bars & subscribe live streaming updates
  useEffect(() => {
    let isSubscribed = true;
    const datafeed = TradingViewDataFeed.getInstance();
    const symbolInfo = buildSymbolInfo(symbol);
    const resolution = TimeframeManager.goatTimeframeToResolution(timeframe);
    const subId = `sub_${panelId}_${symbol}_${resolution}`;
    subscriberIdRef.current = subId;

    // Reset bars state on symbol/timeframe change
    setBars([]);
    barsRef.current = [];

    // 1. Fetch historical bars from REST API
    datafeed.getBars(
      symbolInfo,
      resolution,
      { from: 0, to: Math.floor(Date.now() / 1000), firstDataRequest: true },
      (fetchedBars) => {
        if (!isSubscribed) return;
        barsRef.current = fetchedBars;
        setBars([...fetchedBars]);
      },
      () => {}
    );

    // 2. Subscribe to realtime bar updates (DataFeed now provides full OHLC bars)
    datafeed.subscribeBars(
      symbolInfo,
      resolution,
      (bar: BarData) => {
        if (!isSubscribed) return;

        const prev = barsRef.current;
        if (prev.length === 0) {
          barsRef.current = [bar];
          setBars([bar]);
          return;
        }

        const lastIdx = prev.length - 1;
        const lastBar = prev[lastIdx];

        if (lastBar.time === bar.time) {
          // Merge tick update into existing forming bar (preserve historical open & expand high/low bounds)
          const mergedBar: BarData = {
            time: lastBar.time,
            open: lastBar.open,
            high: Math.max(lastBar.high, bar.high),
            low: Math.min(lastBar.low, bar.low),
            close: bar.close,
            volume: Math.max(lastBar.volume, bar.volume),
          };
          prev[lastIdx] = mergedBar;
          setBars([...prev]);
        } else if (bar.time > lastBar.time) {
          // New candle — append
          prev.push(bar);
          barsRef.current = prev;
          setBars([...prev]);
        }
        // Ignore stale bars (bar.time < lastBar.time)
      },
      subId,
      () => {
        // Reset cache callback — refetch history
        if (isSubscribed) {
          barsRef.current = [];
          setBars([]);
        }
      }
    );

    return () => {
      isSubscribed = false;
      datafeed.unsubscribeBars(subId);
    };
  }, [symbol, timeframe, panelId, buildSymbolInfo]);

  return (
    <ChartContainer
      bars={bars}
      symbol={symbol}
      timeframe={timeframe}
      theme={theme === 'bloomberg' ? 'bloomberg' : theme === 'light' ? 'light' : 'dark'}
      height={height}
      activePositions={activePositions}
      bidPrice={bidPrice}
      askPrice={askPrice}
      lastPrice={lastPrice}
      chartSettings={chartSettings}
      onCrosshairMove={onCrosshairMove}
    />
  );
};
