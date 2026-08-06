/**
 * Project GOAT v1.0 — Production TradingView Lightweight Charts Container
 * Stage 1 Architecture Stabilization & Lightweight Charts Migration (v5.2 Engine)
 *
 * Implements:
 * - Native Lightweight Charts createChart & CandlestickSeries engine
 * - Candlestick series setData & update
 * - Native createPriceLine for Last Price, Bid, Ask, Entry, SL, TP
 * - Auto-resizing ResizeObserver
 * - Theme & layout management
 * - Zero React re-renders on WebSocket tick updates
 */

import React, { useEffect, useRef } from 'react';
import {
  createChart,
  CandlestickSeries,
  createSeriesMarkers,
  IChartApi,
  ISeriesApi,
  IPriceLine,
  CandlestickData,
  Time,
  LineStyle,
  SeriesMarker,
} from 'lightweight-charts';
import { BarData } from './TradingViewDataFeed';
import { Position } from '../components/widgets/OrderTicketWidget';
import { InstitutionalOverlayManager } from './InstitutionalOverlay';
import { ChartSettings, defaultChartSettings } from './ChartSettings';

export interface ChartContainerProps {
  bars: BarData[];
  symbol: string;
  timeframe: string;
  theme?: 'dark' | 'light' | 'bloomberg';
  activePositions?: Position[];
  bidPrice?: number;
  askPrice?: number;
  lastPrice?: number;
  chartSettings?: ChartSettings;
  onCrosshairMove?: (price: number | null, time: number | null) => void;
  height?: number | string;
}

export const ChartContainer: React.FC<ChartContainerProps> = ({
  bars,
  symbol,
  timeframe,
  theme = 'dark',
  activePositions = [],
  bidPrice,
  askPrice,
  lastPrice,
  chartSettings = defaultChartSettings,
  onCrosshairMove,
  height = '100%',
}) => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null);

  // Price lines refs
  const priceLinesRef = useRef<{ [key: string]: IPriceLine }>({});

  // Theme palettes
  const getThemeColors = (t: string) => {
    if (t === 'bloomberg') {
      return {
        bg: '#040d1a',
        text: '#94a3b8',
        grid: '#0f172a',
        up: '#00f0ff',
        down: '#f43f5e',
      };
    }
    if (t === 'light') {
      return {
        bg: '#ffffff',
        text: '#334155',
        grid: '#f1f5f9',
        up: '#10b981',
        down: '#f43f5e',
      };
    }
    // Default dark
    return {
      bg: '#06090e',
      text: '#94a3b8',
      grid: 'rgba(30, 41, 59, 0.5)',
      up: '#10b981',
      down: '#f43f5e',
    };
  };

  // Helper to convert GOAT timestamp to Lightweight Charts Time format
  const toChartTime = (timestampMs: number): Time => {
    const epochSec = timestampMs > 2000000000 ? Math.floor(timestampMs / 1000) : timestampMs;
    return epochSec as Time;
  };

  // Convert BarData array to CandlestickData array
  const toCandlestickData = (barList: BarData[]): CandlestickData<Time>[] => {
    const timeMap = new Map<number, CandlestickData<Time>>();
    barList.forEach((b) => {
      const t = toChartTime(b.time) as number;
      timeMap.set(t, {
        time: t as Time,
        open: b.open,
        high: b.high,
        low: b.low,
        close: b.close,
      });
    });

    return Array.from(timeMap.values()).sort((a, b) => (a.time as number) - (b.time as number));
  };

  // 1. Initialize Chart Instance & Setup Series
  useEffect(() => {
    if (!chartContainerRef.current) return;

    const colors = getThemeColors(theme);

    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: chartContainerRef.current.clientHeight || 400,
      layout: {
        background: { color: colors.bg },
        textColor: colors.text,
        fontSize: 11,
        fontFamily: 'monospace',
      },
      grid: {
        vertLines: { color: colors.grid },
        horzLines: { color: colors.grid },
      },
      crosshair: {
        mode: 1, // Normal crosshair
        vertLine: {
          color: '#38bdf8',
          width: 1,
          style: LineStyle.Dashed,
          labelBackgroundColor: '#0284c7',
        },
        horzLine: {
          color: '#38bdf8',
          width: 1,
          style: LineStyle.Dashed,
          labelBackgroundColor: '#0284c7',
        },
      },
      rightPriceScale: {
        borderColor: colors.grid,
        scaleMargins: {
          top: 0.1,
          bottom: 0.15,
        },
      },
      timeScale: {
        borderColor: colors.grid,
        timeVisible: true,
        secondsVisible: true,
      },
    });

    const series = chart.addSeries(CandlestickSeries, {
      upColor: colors.up,
      downColor: colors.down,
      borderVisible: false,
      wickUpColor: colors.up,
      wickDownColor: colors.down,
    });

    chartRef.current = chart;
    seriesRef.current = series;

    // Crosshair listener
    chart.subscribeCrosshairMove((param) => {
      if (!onCrosshairMove) return;
      if (!param.point || !param.time || param.point.x < 0 || param.point.y < 0) {
        onCrosshairMove(null, null);
        return;
      }
      const price = param.seriesData.get(series) as CandlestickData<Time> | undefined;
      const priceVal = price ? price.close : null;
      const timeVal = typeof param.time === 'number' ? param.time * 1000 : null;
      onCrosshairMove(priceVal, timeVal);
    });

    // ResizeObserver for zero-flicker auto-resizing
    const resizeObserver = new ResizeObserver((entries) => {
      if (entries.length === 0 || !entries[0].contentRect) return;
      const { width: newWidth, height: newHeight } = entries[0].contentRect;
      chart.applyOptions({ width: newWidth, height: newHeight });
    });

    resizeObserver.observe(chartContainerRef.current);

    return () => {
      resizeObserver.disconnect();
      chart.remove();
      chartRef.current = null;
      seriesRef.current = null;
    };
  }, [theme]);

  // 2. Set Data & Update Overlay Layer when `bars` or `chartSettings` changes (Task 8: Independent Layer Plugin)
  useEffect(() => {
    const series = seriesRef.current;
    if (!series || bars.length === 0) return;

    // Candlestick Layer: Update OHLC data
    const formattedBars = toCandlestickData(bars);
    series.setData(formattedBars);

    // Overlay Layer: Apply markers only when enabled via chartSettings (dormant by default: Task 3)
    try {
      const overlayMarkers = InstitutionalOverlayManager.generateOverlayMarkers(bars, chartSettings) as SeriesMarker<Time>[];
      createSeriesMarkers(series, overlayMarkers);
    } catch (e) {
      // Markers fallback
    }
  }, [bars, chartSettings]);

  // 3. Update Native Price Lines for Bid, Ask, Last Price, and Open Positions
  useEffect(() => {
    const series = seriesRef.current;
    if (!series) return;

    // Clear existing price lines
    Object.values(priceLinesRef.current).forEach((line) => {
      try {
        series.removePriceLine(line);
      } catch (e) {
        // Line already removed
      }
    });
    priceLinesRef.current = {};

    // Native Last Price Line
    if (lastPrice && lastPrice > 0) {
      priceLinesRef.current['last'] = series.createPriceLine({
        price: lastPrice,
        color: '#00f0ff',
        lineWidth: 1,
        lineStyle: LineStyle.Dashed,
        axisLabelVisible: true,
        title: `LAST ${lastPrice.toFixed(2)}`,
      });
    }

    // Native Bid / Ask Lines
    if (bidPrice && bidPrice > 0) {
      priceLinesRef.current['bid'] = series.createPriceLine({
        price: bidPrice,
        color: '#10b981',
        lineWidth: 1,
        lineStyle: LineStyle.Dotted,
        axisLabelVisible: true,
        title: `BID ${bidPrice.toFixed(2)}`,
      });
    }

    if (askPrice && askPrice > 0) {
      priceLinesRef.current['ask'] = series.createPriceLine({
        price: askPrice,
        color: '#f43f5e',
        lineWidth: 1,
        lineStyle: LineStyle.Dotted,
        axisLabelVisible: true,
        title: `ASK ${askPrice.toFixed(2)}`,
      });
    }

    // Native Position Price Lines (Entry, SL, TP)
    activePositions.forEach((pos) => {
      // Entry Line
      priceLinesRef.current[`pos_entry_${pos.id}`] = series.createPriceLine({
        price: pos.entryPrice,
        color: pos.type === 'BUY' ? '#10b981' : '#f43f5e',
        lineWidth: 2,
        lineStyle: LineStyle.Solid,
        axisLabelVisible: true,
        title: `${pos.type} ${pos.quantity}L @ ${pos.entryPrice.toFixed(2)} (P/L: $${pos.pnl.toFixed(2)})`,
      });

      // Stop Loss Line
      if (pos.stopLoss) {
        priceLinesRef.current[`pos_sl_${pos.id}`] = series.createPriceLine({
          price: pos.stopLoss,
          color: '#f43f5e',
          lineWidth: 1,
          lineStyle: LineStyle.Dashed,
          axisLabelVisible: true,
          title: `SL ${pos.stopLoss.toFixed(2)}`,
        });
      }

      // Take Profit Line
      if (pos.takeProfit) {
        priceLinesRef.current[`pos_tp_${pos.id}`] = series.createPriceLine({
          price: pos.takeProfit,
          color: '#10b981',
          lineWidth: 1,
          lineStyle: LineStyle.Dashed,
          axisLabelVisible: true,
          title: `TP ${pos.takeProfit.toFixed(2)}`,
        });
      }
    });
  }, [lastPrice, bidPrice, askPrice, activePositions]);

  const latestBar = bars.length > 0 ? bars[bars.length - 1] : null;

  return (
    <div className="relative w-full h-full select-none overflow-hidden" style={{ height }}>
      {/* Legend Overlay Header */}
      <div className="absolute top-2 left-3 z-10 flex items-center space-x-3 text-xs font-mono bg-slate-950/80 px-3 py-1.5 rounded border border-slate-800 backdrop-blur pointer-events-none">
        <span className="font-bold text-slate-100">{symbol}</span>
        <span className="text-cyan-400 font-semibold">{timeframe}</span>
        {latestBar && (
          <div className="flex items-center space-x-2 text-[11px] text-slate-300">
            <span>O: <span className="text-slate-100">{latestBar.open}</span></span>
            <span>H: <span className="text-slate-100">{latestBar.high}</span></span>
            <span>L: <span className="text-slate-100">{latestBar.low}</span></span>
            <span>C: <span className={latestBar.close >= latestBar.open ? 'text-emerald-400 font-bold' : 'text-rose-400 font-bold'}>{latestBar.close}</span></span>
          </div>
        )}
      </div>

      {/* Main Lightweight Charts Container */}
      <div ref={chartContainerRef} className="w-full h-full" />
    </div>
  );
};
