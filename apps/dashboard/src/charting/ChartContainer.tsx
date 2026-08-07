/**
 * Project GOAT v1.1 — Production TradingView Lightweight Charts Container
 * TradingView Candlestick Production Audit — Performance & Visual Fidelity Fix
 *
 * Fixes applied:
 * - series.update() for realtime ticks instead of full setData() per tick
 * - Chart recreation on symbol/timeframe change (not just theme)
 * - Candle borders enabled (TradingView visual fidelity)
 * - Crosshair mode 0 (Magnet) matching TradingView default
 * - Proper priceFormat with precision from SymbolManager
 * - Formatted OHLC legend with correct decimal places
 * - ResizeObserver auto-resizing
 * - Native createPriceLine for Last Price, Bid, Ask, Entry, SL, TP
 */

import React, { useEffect, useRef, useCallback } from 'react';
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
  CrosshairMode,
} from 'lightweight-charts';
import { BarData } from './TradingViewDataFeed';
import { SymbolManager } from './SymbolManager';
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

  // Track last bar count to distinguish initial load from realtime updates
  const prevBarsLengthRef = useRef<number>(0);
  const initializedRef = useRef<boolean>(false);

  // Price lines refs
  const priceLinesRef = useRef<{ [key: string]: IPriceLine }>({});

  // Get symbol metadata for precision formatting
  const symbolMeta = SymbolManager.getSymbolMetadata(symbol);
  const precision = symbolMeta.pipSize;

  // Theme palettes
  const getThemeColors = useCallback((t: string) => {
    if (t === 'bloomberg') {
      return {
        bg: '#040d1a',
        text: '#94a3b8',
        grid: '#0f172a',
        up: '#00f0ff',
        down: '#f43f5e',
        borderUp: '#00d4e0',
        borderDown: '#e11d48',
        wickUp: '#00f0ff',
        wickDown: '#f43f5e',
      };
    }
    if (t === 'light') {
      return {
        bg: '#ffffff',
        text: '#334155',
        grid: '#f1f5f9',
        up: '#26a69a',
        down: '#ef5350',
        borderUp: '#26a69a',
        borderDown: '#ef5350',
        wickUp: '#26a69a',
        wickDown: '#ef5350',
      };
    }
    // Default dark — matching TradingView dark theme
    return {
      bg: '#131722',
      text: '#d1d4dc',
      grid: 'rgba(42, 46, 57, 0.5)',
      up: '#26a69a',
      down: '#ef5350',
      borderUp: '#26a69a',
      borderDown: '#ef5350',
      wickUp: '#26a69a',
      wickDown: '#ef5350',
    };
  }, []);

  // Helper to convert timestamp to Lightweight Charts Time format (seconds)
  const toChartTime = useCallback((timestampMs: number): Time => {
    const epochSec = timestampMs > 2000000000 ? Math.floor(timestampMs / 1000) : timestampMs;
    return epochSec as Time;
  }, []);

  // Convert single BarData to CandlestickData
  const barToCandlestick = useCallback((b: BarData): CandlestickData<Time> => {
    return {
      time: toChartTime(b.time),
      open: b.open,
      high: b.high,
      low: b.low,
      close: b.close,
    };
  }, [toChartTime]);

  // Convert BarData array to sorted, deduplicated CandlestickData array
  const toCandlestickData = useCallback((barList: BarData[]): CandlestickData<Time>[] => {
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
  }, [toChartTime]);

  // 1. Initialize Chart Instance & Setup Series — recreate on theme/symbol/timeframe change
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
        fontFamily: "'Trebuchet MS', Roboto, Ubuntu, sans-serif",
      },
      grid: {
        vertLines: { color: colors.grid },
        horzLines: { color: colors.grid },
      },
      crosshair: {
        mode: CrosshairMode.Normal,
        vertLine: {
          color: '#758696',
          width: 1,
          style: LineStyle.Dashed,
          labelBackgroundColor: '#2B2B43',
        },
        horzLine: {
          color: '#758696',
          width: 1,
          style: LineStyle.Dashed,
          labelBackgroundColor: '#2B2B43',
        },
      },
      rightPriceScale: {
        borderColor: 'rgba(197, 203, 206, 0.1)',
        scaleMargins: {
          top: 0.1,
          bottom: 0.08,
        },
      },
      timeScale: {
        borderColor: 'rgba(197, 203, 206, 0.1)',
        timeVisible: true,
        secondsVisible: true,
        rightOffset: 5,
        barSpacing: 6,
        minBarSpacing: 2,
      },
    });

    // Create candlestick series with TradingView-matching colors
    const series = chart.addSeries(CandlestickSeries, {
      upColor: colors.up,
      downColor: colors.down,
      borderVisible: true,
      borderUpColor: colors.borderUp,
      borderDownColor: colors.borderDown,
      wickUpColor: colors.wickUp,
      wickDownColor: colors.wickDown,
      priceFormat: {
        type: 'price',
        precision: precision,
        minMove: 1 / Math.pow(10, precision),
      },
    });

    chartRef.current = chart;
    seriesRef.current = series;
    initializedRef.current = false;
    prevBarsLengthRef.current = 0;

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
      initializedRef.current = false;
      prevBarsLengthRef.current = 0;
    };
    // Recreate chart when theme, symbol, or timeframe changes
  }, [theme, symbol, timeframe, precision, getThemeColors, onCrosshairMove]);

  // 2. Data Management — setData for initial load, update() for streaming ticks
  useEffect(() => {
    const series = seriesRef.current;
    if (!series || bars.length === 0) return;

    if (!initializedRef.current) {
      // Initial load — full setData
      const formattedBars = toCandlestickData(bars);
      series.setData(formattedBars);
      initializedRef.current = true;
      prevBarsLengthRef.current = bars.length;

      // Fit content on initial load
      const chart = chartRef.current;
      if (chart) {
        chart.timeScale().fitContent();
      }
    } else {
      // Streaming update — only update the last bar or append new bar
      const lastBar = bars[bars.length - 1];
      if (lastBar) {
        const candlestick = barToCandlestick(lastBar);
        series.update(candlestick);
      }
    }

    // Overlay markers (dormant by default)
    try {
      const overlayMarkers = InstitutionalOverlayManager.generateOverlayMarkers(bars, chartSettings) as SeriesMarker<Time>[];
      createSeriesMarkers(series, overlayMarkers);
    } catch {
      // Markers fallback
    }
  }, [bars, chartSettings, toCandlestickData, barToCandlestick]);

  // 3. Update Native Price Lines for Bid, Ask, Last Price, and Open Positions
  useEffect(() => {
    const series = seriesRef.current;
    if (!series) return;

    // Clear existing price lines
    Object.values(priceLinesRef.current).forEach((line) => {
      try {
        series.removePriceLine(line);
      } catch {
        // Line already removed
      }
    });
    priceLinesRef.current = {};

    // Native Last Price Line
    if (lastPrice && lastPrice > 0) {
      priceLinesRef.current['last'] = series.createPriceLine({
        price: lastPrice,
        color: '#2962FF',
        lineWidth: 1,
        lineStyle: LineStyle.Dashed,
        axisLabelVisible: true,
        title: `LAST ${lastPrice.toFixed(precision)}`,
      });
    }

    // Native Bid / Ask Lines
    if (bidPrice && bidPrice > 0) {
      priceLinesRef.current['bid'] = series.createPriceLine({
        price: bidPrice,
        color: '#26a69a',
        lineWidth: 1,
        lineStyle: LineStyle.Dotted,
        axisLabelVisible: true,
        title: `BID ${bidPrice.toFixed(precision)}`,
      });
    }

    if (askPrice && askPrice > 0) {
      priceLinesRef.current['ask'] = series.createPriceLine({
        price: askPrice,
        color: '#ef5350',
        lineWidth: 1,
        lineStyle: LineStyle.Dotted,
        axisLabelVisible: true,
        title: `ASK ${askPrice.toFixed(precision)}`,
      });
    }

    // Native Position Price Lines (Entry, SL, TP)
    activePositions.forEach((pos) => {
      priceLinesRef.current[`pos_entry_${pos.id}`] = series.createPriceLine({
        price: pos.entryPrice,
        color: pos.type === 'BUY' ? '#26a69a' : '#ef5350',
        lineWidth: 2,
        lineStyle: LineStyle.Solid,
        axisLabelVisible: true,
        title: `${pos.type} ${pos.quantity}L @ ${pos.entryPrice.toFixed(precision)} (P/L: $${pos.pnl.toFixed(2)})`,
      });

      if (pos.stopLoss) {
        priceLinesRef.current[`pos_sl_${pos.id}`] = series.createPriceLine({
          price: pos.stopLoss,
          color: '#ef5350',
          lineWidth: 1,
          lineStyle: LineStyle.Dashed,
          axisLabelVisible: true,
          title: `SL ${pos.stopLoss.toFixed(precision)}`,
        });
      }

      if (pos.takeProfit) {
        priceLinesRef.current[`pos_tp_${pos.id}`] = series.createPriceLine({
          price: pos.takeProfit,
          color: '#26a69a',
          lineWidth: 1,
          lineStyle: LineStyle.Dashed,
          axisLabelVisible: true,
          title: `TP ${pos.takeProfit.toFixed(precision)}`,
        });
      }
    });
  }, [lastPrice, bidPrice, askPrice, activePositions, precision]);

  const latestBar = bars.length > 0 ? bars[bars.length - 1] : null;

  return (
    <div className="relative w-full h-full select-none overflow-hidden" style={{ height }}>
      {/* Legend Overlay Header — matching TradingView OHLC format */}
      <div className="absolute top-2 left-3 z-10 flex items-center space-x-3 text-xs font-mono bg-slate-950/80 px-3 py-1.5 rounded border border-slate-800 backdrop-blur pointer-events-none">
        <span className="font-bold text-slate-100">{symbol}</span>
        <span className="text-cyan-400 font-semibold">{timeframe}</span>
        {latestBar && (
          <div className="flex items-center space-x-2 text-[11px] text-slate-300">
            <span>O: <span className="text-slate-100">{latestBar.open.toFixed(precision)}</span></span>
            <span>H: <span className="text-slate-100">{latestBar.high.toFixed(precision)}</span></span>
            <span>L: <span className="text-slate-100">{latestBar.low.toFixed(precision)}</span></span>
            <span>C: <span className={latestBar.close >= latestBar.open ? 'text-emerald-400 font-bold' : 'text-rose-400 font-bold'}>{latestBar.close.toFixed(precision)}</span></span>
          </div>
        )}
      </div>

      {/* Main Lightweight Charts Container */}
      <div ref={chartContainerRef} className="w-full h-full" />
    </div>
  );
};
