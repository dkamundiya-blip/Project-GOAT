/**
 * Project GOAT v1.0 — TradingView Interactive Canvas/SVG Chart Widget
 * Step 1.6 Institutional TradingView Charting Engine
 *
 * Full TradingView-grade Interactive Renderer:
 * - 200–300 historical candles display
 * - Smooth Mouse Wheel Zoom (1.8px to 35px candle spacing)
 * - Drag-to-Pan horizontal history scrolling
 * - Double-click auto-fit reset
 * - Visible-range auto-adjusting Y-axis price scale
 * - X-axis Time scale with intraday & daily timestamp formatting
 * - Synchronized Crosshair with Price (Y-axis) & Time (X-axis) badges
 * - Last price dashed line & live price tag
 * - Strict OHLC live tick streaming aggregation & timeframe boundary handling
 */

import React, { useRef, useEffect, useState, useCallback } from 'react';
import { SymbolManager } from './SymbolManager';
import { TimeframeManager } from './TimeframeManager';
import { TradingViewDataFeed, BarData } from './TradingViewDataFeed';
import { ChartStyleType, CrosshairModeType, ThemeType } from './ChartState';
import { DrawingToolType } from './DrawingManager';
import { CrosshairManager } from './CrosshairManager';

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
  onCrosshairMove?: (price: number | null, time: number | null) => void;
}

export const TradingViewWidget: React.FC<TradingViewWidgetProps> = ({
  panelId = 'panel_primary',
  symbol,
  timeframe,
  chartStyle = 'candlestick',
  crosshairMode = 'normal',
  theme = 'dark',
  height = '100%',
  showVolume = true,
  showGridLines = true,
  onCrosshairMove,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const [bars, setBars] = useState<BarData[]>([]);
  const [crosshairPos, setCrosshairPos] = useState<{ x: number; y: number; price: number; time: number } | null>(null);

  // Interactive Zoom & Pan Refs
  const zoomSpacingRef = useRef<number>(6.5); // barSpacing in pixels
  const panOffsetRef = useRef<number>(0);     // 0 = live edge, >0 = panned back into history
  const isDraggingRef = useRef<boolean>(false);
  const dragStartXRef = useRef<number>(0);
  const dragStartPanRef = useRef<number>(0);

  const datafeedRef = useRef<TradingViewDataFeed>(new TradingViewDataFeed());

  // Format timestamp for bottom X-axis
  const formatTimeLabel = (timestampMs: number, tf: string): string => {
    const d = new Date(timestampMs);
    if (isNaN(d.getTime())) return '';
    const hours = d.getUTCHours().toString().padStart(2, '0');
    const mins = d.getUTCMinutes().toString().padStart(2, '0');
    const secs = d.getUTCSeconds().toString().padStart(2, '0');

    if (tf === '1D' || tf === '4H') {
      const month = d.toLocaleString('en-US', { month: 'short', timeZone: 'UTC' });
      const day = d.getUTCDate().toString().padStart(2, '0');
      return `${month} ${day}`;
    }
    return `${hours}:${mins}:${secs}`;
  };

  // Load bars when symbol or timeframe changes
  useEffect(() => {
    let isSubscribed = true;
    setBars([]);
    panOffsetRef.current = 0; // Reset pan on symbol/timeframe switch

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

    datafeedRef.current.getBars(
      symbolInfo,
      resolution,
      { from: 0, to: Math.floor(Date.now() / 1000), firstDataRequest: true },
      (fetchedBars) => {
        if (isSubscribed) {
          console.log('[TradingViewWidget] Loaded initial bars count for', symbol, fetchedBars.length);
          setBars(fetchedBars);
        }
      },
      () => {}
    );

    // Subscribe live streaming updates with strict OHLC candle aggregation
    datafeedRef.current.subscribeBars(
      symbolInfo,
      resolution,
      (update: any) => {
        if (!isSubscribed) return;
        setBars((prev) => {
          // 1. If update is already a full BarData object (from REST polling fallback):
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

          // 2. If update is a live tick frame { symbol, time, price }:
          const tickPrice = Number(update.price);
          const tickTime = Number(update.time);
          if (isNaN(tickPrice) || isNaN(tickTime)) return prev;

          if (prev.length === 0) {
            return [{
              time: tickTime,
              open: tickPrice,
              high: tickPrice,
              low: tickPrice,
              close: tickPrice,
              volume: 1,
            }];
          }

          const last = prev[prev.length - 1];
          if (last.time === tickTime) {
            // Same timeframe interval -> Update current open candle according to OHLC rules
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
            // Timeframe boundary crossed -> Finalize open candle & open new forming candle
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

  // Subscribe to CrosshairManager
  useEffect(() => {
    return CrosshairManager.subscribe((pos) => {
      if (pos && pos.sourcePanelId !== panelId && pos.price !== null && pos.time !== null) {
        // Sync external crosshair
      }
    });
  }, [panelId]);

  // Render Canvas Chart (60 FPS high performance)
  const drawChart = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas || bars.length === 0) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const width = canvas.width;
    const heightVal = canvas.height;

    // Theme color palette
    const bg = theme === 'bloomberg' ? '#040d1a' : theme === 'light' ? '#ffffff' : '#06090e';
    const gridColor = theme === 'light' ? 'rgba(200, 200, 200, 0.4)' : 'rgba(30, 41, 59, 0.5)';
    const textColor = theme === 'light' ? '#334155' : '#94a3b8';
    const greenUp = '#10b981';
    const redDown = '#f43f5e';

    // Clear Canvas
    ctx.fillStyle = bg;
    ctx.fillRect(0, 0, width, heightVal);

    // Layout Margins
    const rightMargin = 65;      // Y-axis width
    const timeAxisHeight = 24;   // X-axis height
    const availableWidth = width - rightMargin;
    const availableHeight = heightVal - timeAxisHeight;

    const chartTop = 24;
    const chartBottom = showVolume ? availableHeight - 45 : availableHeight - 10;
    const chartHeight = Math.max(10, chartBottom - chartTop);

    // Zoom & Pan Spacing
    const barSpacing = zoomSpacingRef.current;
    const candleWidth = Math.max(1, Math.min(24, Math.floor(barSpacing * 0.75)));
    const maxVisibleCount = Math.floor(availableWidth / barSpacing);

    // Pan clamping: panOffsetRef cannot exceed total bars or be negative
    const maxPan = Math.max(0, bars.length - Math.floor(maxVisibleCount / 2));
    panOffsetRef.current = Math.max(0, Math.min(maxPan, panOffsetRef.current));
    const panOffset = panOffsetRef.current;

    // Determine slice of visible bars
    const endIndex = Math.max(1, bars.length - panOffset);
    const startIndex = Math.max(0, endIndex - maxVisibleCount);
    const visibleBars = bars.slice(startIndex, endIndex);

    if (visibleBars.length === 0) return;

    // Compute Price Bounds strictly from visible candle range
    let minPrice = Infinity;
    let maxPrice = -Infinity;
    let maxVol = 0;

    for (const b of visibleBars) {
      if (b.low < minPrice) minPrice = b.low;
      if (b.high > maxPrice) maxPrice = b.high;
      if (b.volume > maxVol) maxVol = b.volume;
    }

    const priceRange = maxPrice - minPrice;
    const pricePadding = priceRange === 0 ? (maxPrice === 0 ? 1.0 : Math.abs(maxPrice) * 0.05 || 1.0) : priceRange * 0.05;
    const scaledMinPrice = minPrice - pricePadding;
    const scaledMaxPrice = maxPrice + pricePadding;
    const totalRange = scaledMaxPrice - scaledMinPrice;

    const priceToY = (p: number) => {
      if (totalRange <= 0) return chartTop + chartHeight / 2;
      return chartBottom - ((p - scaledMinPrice) / totalRange) * chartHeight;
    };

    // 1. Draw Grid Lines & Price Axis (Y-axis)
    if (showGridLines) {
      ctx.strokeStyle = gridColor;
      ctx.lineWidth = 1;

      // Horizontal Price Grid Lines
      const priceSteps = 6;
      for (let i = 0; i <= priceSteps; i++) {
        const y = chartTop + (chartHeight / priceSteps) * i;
        const priceVal = scaledMaxPrice - (totalRange / priceSteps) * i;

        ctx.beginPath();
        ctx.moveTo(0, Math.floor(y) + 0.5);
        ctx.lineTo(availableWidth, Math.floor(y) + 0.5);
        ctx.stroke();

        // Y-Axis Price Label
        ctx.fillStyle = textColor;
        ctx.font = '10px monospace';
        ctx.fillText(SymbolManager.formatPrice(priceVal, symbol), availableWidth + 6, y + 3);
      }
    }

    // 2. Draw X-Axis Time Labels & Vertical Grid Lines
    const timeLabelStep = Math.max(1, Math.floor(80 / barSpacing));
    visibleBars.forEach((bar, idx) => {
      const x = Math.floor(availableWidth - (visibleBars.length - 1 - idx) * barSpacing - barSpacing / 2) + 0.5;

      if (idx % timeLabelStep === 0 && x >= 0 && x <= availableWidth) {
        if (showGridLines) {
          ctx.strokeStyle = gridColor;
          ctx.lineWidth = 1;
          ctx.beginPath();
          ctx.moveTo(x, chartTop);
          ctx.lineTo(x, availableHeight);
          ctx.stroke();
        }

        // X-Axis Time Label
        ctx.fillStyle = textColor;
        ctx.font = '10px monospace';
        ctx.fillText(formatTimeLabel(bar.time, timeframe), x - 20, heightVal - 6);
      }
    });

    // 3. Draw Chart Bars & Candlesticks
    visibleBars.forEach((bar, idx) => {
      const x = Math.floor(availableWidth - (visibleBars.length - 1 - idx) * barSpacing - barSpacing / 2) + 0.5;
      const isUp = bar.close >= bar.open;
      const color = isUp ? greenUp : redDown;

      if (chartStyle === 'line') {
        const y = priceToY(bar.close);
        if (idx === 0) {
          ctx.beginPath();
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
        if (idx === visibleBars.length - 1) {
          ctx.strokeStyle = '#00f0ff';
          ctx.lineWidth = 2;
          ctx.stroke();
        }
      } else if (chartStyle === 'area') {
        const y = priceToY(bar.close);
        if (idx === 0) {
          ctx.beginPath();
          ctx.moveTo(x, chartBottom);
          ctx.lineTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
        if (idx === visibleBars.length - 1) {
          ctx.lineTo(x, chartBottom);
          ctx.closePath();
          const grad = ctx.createLinearGradient(0, chartTop, 0, chartBottom);
          grad.addColorStop(0, 'rgba(0, 240, 255, 0.4)');
          grad.addColorStop(1, 'rgba(0, 240, 255, 0.0)');
          ctx.fillStyle = grad;
          ctx.fill();
        }
      } else {
        // Candlestick / Heikin Ashi / Renko
        const yOpen = priceToY(bar.open);
        const yClose = priceToY(bar.close);
        const yHigh = priceToY(bar.high); // Smallest Y (highest price)
        const yLow = priceToY(bar.low);   // Largest Y (lowest price)

        // Draw Wick (high to low)
        ctx.strokeStyle = color;
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(x, Math.min(yHigh, yLow));
        ctx.lineTo(x, Math.max(yHigh, yLow));
        ctx.stroke();

        // Draw Body (open to close)
        ctx.fillStyle = color;
        const bodyTop = Math.min(yOpen, yClose);
        const rawBodyHeight = Math.abs(yClose - yOpen);

        if (rawBodyHeight < 1) {
          // Doji or equal open/close -> Render 1px thin horizontal line
          ctx.fillRect(x - candleWidth / 2, bodyTop, candleWidth, 1);
        } else {
          // Normal candle body -> Render body rectangle
          ctx.fillRect(x - candleWidth / 2, bodyTop, candleWidth, rawBodyHeight);
        }
      }

      // Draw Volume Bars
      if (showVolume && maxVol > 0) {
        const volY = availableHeight - (bar.volume / maxVol) * 40;
        ctx.fillStyle = isUp ? 'rgba(16, 185, 129, 0.25)' : 'rgba(244, 63, 94, 0.25)';
        ctx.fillRect(x - candleWidth / 2, volY, candleWidth, availableHeight - volY);
      }
    });

    // 4. Draw Latest Price Line & Tag
    const latestBar = bars[bars.length - 1];
    if (latestBar) {
      const lastY = Math.floor(priceToY(latestBar.close)) + 0.5;
      const isUp = latestBar.close >= latestBar.open;
      const tagColor = isUp ? greenUp : redDown;

      // Dashed horizontal price line
      ctx.strokeStyle = tagColor;
      ctx.setLineDash([3, 3]);
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(0, lastY);
      ctx.lineTo(availableWidth, lastY);
      ctx.stroke();
      ctx.setLineDash([]);

      // Y-Axis Live Price Tag Badge
      ctx.fillStyle = tagColor;
      ctx.fillRect(availableWidth, lastY - 9, 63, 18);
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 10px monospace';
      ctx.fillText(SymbolManager.formatPrice(latestBar.close, symbol), availableWidth + 5, lastY + 3);
    }

    // 5. Draw Interactive Crosshair & Badges
    if (crosshairPos && crosshairMode !== 'hidden') {
      ctx.strokeStyle = '#38bdf8';
      ctx.setLineDash([4, 4]);
      ctx.lineWidth = 1;

      // Horizontal Line
      ctx.beginPath();
      ctx.moveTo(0, crosshairPos.y);
      ctx.lineTo(availableWidth, crosshairPos.y);
      ctx.stroke();

      // Vertical Line
      ctx.beginPath();
      ctx.moveTo(crosshairPos.x, chartTop);
      ctx.lineTo(crosshairPos.x, availableHeight);
      ctx.stroke();

      ctx.setLineDash([]);

      // Y-Axis Crosshair Price Badge
      ctx.fillStyle = '#0284c7';
      ctx.fillRect(availableWidth, crosshairPos.y - 10, 63, 20);
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 10px monospace';
      ctx.fillText(SymbolManager.formatPrice(crosshairPos.price, symbol), availableWidth + 5, crosshairPos.y + 3);

      // X-Axis Crosshair Time Badge
      if (crosshairPos.time) {
        const timeText = formatTimeLabel(crosshairPos.time, timeframe);
        ctx.fillStyle = '#0284c7';
        ctx.fillRect(crosshairPos.x - 30, availableHeight, 60, 20);
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 10px monospace';
        ctx.fillText(timeText, crosshairPos.x - 22, availableHeight + 14);
      }
    }
  }, [bars, chartStyle, crosshairPos, crosshairMode, theme, symbol, timeframe, showVolume, showGridLines]);

  // Canvas Resize Listener
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const parent = canvas.parentElement;
    if (!parent) return;

    const handleResize = () => {
      canvas.width = parent.clientWidth;
      canvas.height = parent.clientHeight;
      drawChart();
    };

    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [drawChart]);

  useEffect(() => {
    drawChart();
  }, [drawChart]);

  // Handle Mouse Wheel for Zoom In / Zoom Out
  const handleWheel = (e: React.WheelEvent<HTMLCanvasElement>) => {
    e.preventDefault();
    const zoomFactor = e.deltaY < 0 ? 1.15 : 0.85;
    const newSpacing = Math.max(1.8, Math.min(35, zoomSpacingRef.current * zoomFactor));
    zoomSpacingRef.current = newSpacing;
    drawChart();
  };

  // Handle Mouse Drag for Horizontal Pan
  const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (e.button === 0) { // Left click
      isDraggingRef.current = true;
      dragStartXRef.current = e.clientX;
      dragStartPanRef.current = panOffsetRef.current;
    }
  };

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas || bars.length === 0) return;
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const rightMargin = 65;
    const timeAxisHeight = 24;
    const availableWidth = canvas.width - rightMargin;
    const availableHeight = canvas.height - timeAxisHeight;

    // If dragging, update pan offset
    if (isDraggingRef.current) {
      const deltaX = e.clientX - dragStartXRef.current;
      const deltaBars = Math.round(deltaX / zoomSpacingRef.current);
      panOffsetRef.current = Math.max(0, dragStartPanRef.current + deltaBars);
      drawChart();
      return;
    }

    // Crosshair calculation
    const barSpacing = zoomSpacingRef.current;
    const maxVisibleCount = Math.floor(availableWidth / barSpacing);

    const panOffset = panOffsetRef.current;
    const endIndex = Math.max(1, bars.length - panOffset);
    const startIndex = Math.max(0, endIndex - maxVisibleCount);
    const visibleBars = bars.slice(startIndex, endIndex);

    if (visibleBars.length === 0) return;

    let minPrice = Infinity;
    let maxPrice = -Infinity;
    visibleBars.forEach((b) => {
      if (b.low < minPrice) minPrice = b.low;
      if (b.high > maxPrice) maxPrice = b.high;
    });

    const priceRange = maxPrice - minPrice;
    const pricePadding = priceRange === 0 ? (maxPrice === 0 ? 1.0 : Math.abs(maxPrice) * 0.05 || 1.0) : priceRange * 0.05;
    const scaledMinPrice = minPrice - pricePadding;
    const scaledMaxPrice = maxPrice + pricePadding;
    const totalRange = scaledMaxPrice - scaledMinPrice;

    const chartBottom = showVolume ? availableHeight - 45 : availableHeight - 10;
    const chartTop = 24;
    const chartHeight = Math.max(10, chartBottom - chartTop);

    const price = scaledMaxPrice - ((y - chartTop) / chartHeight) * totalRange;

    // Locate bar under cursor x
    const barOffsetFromRight = Math.floor((availableWidth - x) / barSpacing);
    const barIdx = visibleBars.length - 1 - barOffsetFromRight;
    const clampedIdx = Math.min(visibleBars.length - 1, Math.max(0, barIdx));
    const time = visibleBars[clampedIdx]?.time || Date.now();

    const pos = { x, y, price, time };
    setCrosshairPos(pos);
    CrosshairManager.setPosition({ x, y, price, time, sourcePanelId: panelId });

    if (onCrosshairMove) {
      onCrosshairMove(price, time);
    }
  };

  const handleMouseUp = () => {
    isDraggingRef.current = false;
  };

  const handleMouseLeave = () => {
    isDraggingRef.current = false;
    setCrosshairPos(null);
    CrosshairManager.setPosition(null);
    if (onCrosshairMove) onCrosshairMove(null, null);
  };

  // Double click resets zoom & pan (auto-fit)
  const handleDoubleClick = () => {
    zoomSpacingRef.current = 6.5;
    panOffsetRef.current = 0;
    drawChart();
  };

  const latestBar = bars.length > 0 ? bars[bars.length - 1] : null;

  return (
    <div ref={containerRef} className="relative w-full h-full select-none overflow-hidden" style={{ height }}>
      {/* Legend Header */}
      <div className="absolute top-2 left-3 z-10 flex items-center space-x-3 text-xs font-mono bg-slate-950/80 px-3 py-1.5 rounded border border-slate-800 backdrop-blur">
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

      {/* Interactive Controls Guide */}
      <div className="absolute bottom-7 left-3 z-10 text-[10px] font-mono text-slate-500 bg-slate-950/60 px-2 py-1 rounded border border-slate-900 pointer-events-none">
        Wheel: Zoom | Drag: Pan | Double-Click: Reset
      </div>

      {/* Main Canvas */}
      <canvas
        ref={canvasRef}
        onWheel={handleWheel}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseLeave}
        onDoubleClick={handleDoubleClick}
        className="w-full h-full block cursor-crosshair"
      />
    </div>
  );
};
