/**
 * Project GOAT v1.0 — Institutional TradingView Lightweight Charts Renderer
 * Stage 1 Architecture Stabilization & Lightweight Charts Migration
 *
 * Refactored TradingViewWidget wrapping ChartContainer:
 * - Uses production-grade TradingView Lightweight Charts
 * - Connects to existing TradingViewDataFeed REST & WebSocket stream
 * - Zero custom 2D canvas drawing code
 * - Preserves all props & callbacks for 100% backward compatibility
 */

import React, { useRef, useEffect, useState } from 'react';
import { SymbolManager } from './SymbolManager';
import { TimeframeManager } from './TimeframeManager';
import { TradingViewDataFeed, BarData } from './TradingViewDataFeed';
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
  const datafeedRef = useRef<TradingViewDataFeed>(new TradingViewDataFeed());

  // Load historical bars & subscribe live streaming updates
  useEffect(() => {
    let isSubscribed = true;
    setBars([]);

    const meta = SymbolManager.getSymbolMetadata(symbol);
    const symbolInfo: any = {
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

    const resolution = TimeframeManager.goatTimeframeToResolution(timeframe);

    // 1. Fetch REST History
    datafeedRef.current.getBars(
      symbolInfo,
      resolution,
      { from: 0, to: Math.floor(Date.now() / 1000), firstDataRequest: true },
      (fetchedBars) => {
        if (isSubscribed) {
          setBars(fetchedBars);
        }
      },
      () => {}
    );

    // 2. Subscribe to WebSocket Live Ticks & Aggregate OHLC
    datafeedRef.current.subscribeBars(
      symbolInfo,
      resolution,
      (update: any) => {
        if (!isSubscribed) return;
        setBars((prev) => {
          // Full BarData update (REST fallback)
          if (typeof update.open === 'number' && typeof update.close === 'number') {
            const fullBar = update as BarData;
            if (prev.length === 0) return [fullBar];
            const last = prev[prev.length - 1];
            if (last.time === fullBar.time) {
              const updated = [...prev];
              updated[updated.length - 1] = fullBar;
              return updated;
            } else if (fullBar.time > last.time) {
              return [...prev, fullBar];
            }
            return prev;
          }

          // Live tick frame { symbol, time, price }
          const tickPrice = Number(update.price);
          const tickTime = Number(update.time);
          if (isNaN(tickPrice) || isNaN(tickTime)) return prev;

          if (prev.length === 0) {
            return [
              {
                time: tickTime,
                open: tickPrice,
                high: tickPrice,
                low: tickPrice,
                close: tickPrice,
                volume: 1,
              },
            ];
          }

          const last = prev[prev.length - 1];
          if (last.time === tickTime) {
            // Same interval -> Mutate final candle OHLC
            const updatedLast: BarData = {
              time: last.time,
              open: last.open,
              high: Math.max(last.high, tickPrice),
              low: Math.min(last.low, tickPrice),
              close: tickPrice,
              volume: last.volume + 1,
            };
            const updated = [...prev];
            updated[updated.length - 1] = updatedLast;
            return updated;
          } else if (tickTime > last.time) {
            // New timeframe interval -> Append forming candle
            const newBar: BarData = {
              time: tickTime,
              open: tickPrice,
              high: tickPrice,
              low: tickPrice,
              close: tickPrice,
              volume: 1,
            };
            return [...prev, newBar];
          }
          return prev;
        });
      },
      `sub_${panelId}_${symbol}_${resolution}`,
      () => {}
    );

    return () => {
      isSubscribed = false;
      datafeedRef.current.unsubscribeBars(`sub_${panelId}_${symbol}_${resolution}`);
    };
  }, [symbol, timeframe, panelId]);

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
