/**
 * Project GOAT v1.0 — TradingView Interactive Canvas/SVG Chart Widget
 * Step 1.6 Institutional TradingView Charting Engine
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

  const datafeedRef = useRef<TradingViewDataFeed>(new TradingViewDataFeed());

  // Load bars when symbol or timeframe changes
  useEffect(() => {
    let isSubscribed = true;
    setBars([]); // Clear stale bars to force clean price scale recalculation on symbol/timeframe switch

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

    // Subscribe live streaming updates
    datafeedRef.current.subscribeBars(
      symbolInfo,
      resolution,
      (newBar) => {
        if (!isSubscribed) return;
        console.log('[TradingViewWidget] Stream bar update for', symbol, newBar);
        setBars((prev) => {
          if (prev.length === 0) return [newBar];
          const last = prev[prev.length - 1];
          if (last.time === newBar.time) {
            const updated = [...prev];
            updated[updated.length - 1] = newBar;
            return updated;
          }
          return [...prev, newBar];
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

    // Geometry & Layout Constants
    const rightMargin = 60; // Axis width
    const availableWidth = width - rightMargin;

    // Fixed spacing per candle: 6px to 10px depending on canvas width & candle count
    // Capped body width (max 8px) to eliminate oversized block candles
    const barSpacing = Math.max(3, Math.min(10, availableWidth / Math.max(1, Math.min(bars.length, 120))));
    const candleWidth = Math.max(1, Math.min(8, Math.floor(barSpacing * 0.75)));

    // Visible candle slice
    const maxVisibleCount = Math.floor(availableWidth / barSpacing);
    const visibleBars = bars.slice(-maxVisibleCount);

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

    const chartBottom = showVolume ? heightVal - 60 : heightVal - 30;
    const chartTop = 30;
    const chartHeight = Math.max(10, chartBottom - chartTop);

    const priceToY = (p: number) => {
      if (totalRange <= 0) return chartTop + chartHeight / 2;
      return chartBottom - ((p - scaledMinPrice) / totalRange) * chartHeight;
    };

    console.log('[TradingViewWidget] Canvas rendering debug:', {
      symbol,
      timeframe,
      totalBars: bars.length,
      visibleBarsCount: visibleBars.length,
      barSpacing,
      candleWidth,
      rawMinPrice: minPrice,
      rawMaxPrice: maxPrice,
      scaledMinPrice,
      scaledMaxPrice,
      totalRange,
      chartHeight,
    });

    // Draw Grid Lines
    if (showGridLines) {
      ctx.strokeStyle = gridColor;
      ctx.lineWidth = 1;

      // Horizontal price lines
      const priceSteps = 5;
      for (let i = 0; i <= priceSteps; i++) {
        const y = chartTop + (chartHeight / priceSteps) * i;
        const priceVal = scaledMaxPrice - (totalRange / priceSteps) * i;
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(availableWidth, y);
        ctx.stroke();

        // Price Axis Label
        ctx.fillStyle = textColor;
        ctx.font = '10px monospace';
        ctx.fillText(SymbolManager.formatPrice(priceVal, symbol), availableWidth + 5, y + 3);
      }
    }

    // Draw Chart Bars from right to left with fixed spacing
    visibleBars.forEach((bar, idx) => {
      // Right-aligned candle position
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
          // Normal candle body -> Render body rectangle capped at candleWidth
          ctx.fillRect(x - candleWidth / 2, bodyTop, candleWidth, rawBodyHeight);
        }
      }

      // Draw Volume Bars
      if (showVolume && maxVol > 0) {
        const volY = heightVal - (bar.volume / maxVol) * 45;
        ctx.fillStyle = isUp ? 'rgba(16, 185, 129, 0.25)' : 'rgba(244, 63, 94, 0.25)';
        ctx.fillRect(x - candleWidth / 2, volY, candleWidth, heightVal - volY);
      }
    });

    // Draw Crosshair
    if (crosshairPos && crosshairMode !== 'hidden') {
      ctx.strokeStyle = '#38bdf8';
      ctx.setLineDash([4, 4]);
      ctx.lineWidth = 1;

      // Horizontal
      ctx.beginPath();
      ctx.moveTo(0, crosshairPos.y);
      ctx.lineTo(availableWidth, crosshairPos.y);
      ctx.stroke();

      // Vertical
      ctx.beginPath();
      ctx.moveTo(crosshairPos.x, chartTop);
      ctx.lineTo(crosshairPos.x, chartBottom);
      ctx.stroke();

      ctx.setLineDash([]);

      // Crosshair Price Badge
      ctx.fillStyle = '#0284c7';
      ctx.fillRect(availableWidth, crosshairPos.y - 10, 58, 20);
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 10px monospace';
      ctx.fillText(SymbolManager.formatPrice(crosshairPos.price, symbol), availableWidth + 5, crosshairPos.y + 3);
    }
  }, [bars, chartStyle, crosshairPos, crosshairMode, theme, symbol, showVolume, showGridLines]);

  // Canvas Resize & Animation Loop
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

  // Handle Mouse Move for Crosshair
  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas || bars.length === 0) return;
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const rightMargin = 60;
    const availableWidth = canvas.width - rightMargin;

    const barSpacing = Math.max(3, Math.min(10, availableWidth / Math.max(1, Math.min(bars.length, 120))));
    const maxVisibleCount = Math.floor(availableWidth / barSpacing);
    const visibleBars = bars.slice(-maxVisibleCount);

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

    const chartBottom = showVolume ? canvas.height - 60 : canvas.height - 30;
    const chartTop = 30;
    const chartHeight = Math.max(10, chartBottom - chartTop);

    const price = scaledMaxPrice - ((y - chartTop) / chartHeight) * totalRange;

    // Locate bar under mouse x
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

  const handleMouseLeave = () => {
    setCrosshairPos(null);
    CrosshairManager.setPosition(null);
    if (onCrosshairMove) onCrosshairMove(null, null);
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

      {/* Main Canvas */}
      <canvas
        ref={canvasRef}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
        className="w-full h-full block cursor-crosshair"
      />
    </div>
  );
};
