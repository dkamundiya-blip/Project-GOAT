/**
 * Project GOAT v1.0 — TradingView Charting Workspace Shell Container
 * Step 1.6 Institutional TradingView Charting Engine
 */

import React, { useState } from 'react';
import { useChartStateStore } from './ChartState';
import { SymbolManager } from './SymbolManager';
import { TimeframeManager } from './TimeframeManager';
import { LayoutManager } from './LayoutManager';
import { DrawingManager, DrawingToolType } from './DrawingManager';
import { TradingViewWidget } from './TradingViewWidget';
import {
  BarChart2,
  TrendingUp,
  Activity,
  Layers,
  Grid,
  Maximize2,
  RotateCcw,
  MousePointer,
  Minus,
  MoveUpRight,
  Square,
  Circle,
  Type,
  Ruler,
  Magnet,
  Trash2,
  ChevronDown,
} from 'lucide-react';

export interface TradingViewContainerProps {
  initialSymbol?: string;
  initialTimeframe?: string;
  className?: string;
}

export const TradingViewContainer: React.FC<TradingViewContainerProps> = ({
  initialSymbol = 'VOLATILITY_100',
  initialTimeframe = '1M',
  className = '',
}) => {
  const {
    activeSymbol,
    activeTimeframe,
    chartStyle,
    layoutMode,
    theme,
    isFullscreen,
    isReplayMode,
    showVolume,
    showGridLines,
    setSymbol,
    setTimeframe,
    setChartStyle,
    setLayoutMode,
    toggleFullscreen,
    toggleReplayMode,
  } = useChartStateStore();

  const [activeTool, setActiveTool] = useState<DrawingToolType>('cursor');
  const [drawingMgr] = useState<DrawingManager>(new DrawingManager());
  const [isMagnet, setIsMagnet] = useState<boolean>(false);
  const [symbolMenuOpen, setSymbolMenuOpen] = useState(false);

  const symbols = SymbolManager.getAllSymbols();
  const timeframes = TimeframeManager.getAllTimeframes();
  const panels = LayoutManager.getPanelsForLayout(layoutMode, activeSymbol || initialSymbol, activeTimeframe || initialTimeframe);

  const handleToolSelect = (tool: DrawingToolType) => {
    setActiveTool(tool);
    drawingMgr.setActiveTool(tool);
  };

  const handleMagnetToggle = () => {
    const mag = drawingMgr.toggleMagnetMode();
    setIsMagnet(mag);
  };

  const handleClearDrawings = () => {
    drawingMgr.clearAllDrawings();
  };

  return (
    <div
      className={`flex flex-col bg-[#06090e] border border-slate-800 rounded-xl overflow-hidden shadow-2xl select-none ${
        isFullscreen ? 'fixed inset-0 z-50 rounded-none' : 'w-full h-[650px]'
      } ${className}`}
    >
      {/* Top Main Toolbar */}
      <div className="h-10 bg-[#0b101b] border-b border-slate-800 px-3 flex items-center justify-between text-xs font-mono text-slate-300 z-20">
        <div className="flex items-center space-x-2">
          {/* Symbol Dropdown */}
          <div className="relative">
            <button
              onClick={() => setSymbolMenuOpen(!symbolMenuOpen)}
              className="flex items-center space-x-1.5 bg-slate-900 hover:bg-slate-800 text-slate-100 font-bold px-2.5 py-1 rounded border border-slate-700 transition-colors"
            >
              <span>{activeSymbol || initialSymbol}</span>
              <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
            </button>

            {symbolMenuOpen && (
              <div className="absolute top-8 left-0 w-56 bg-[#090d16] border border-slate-700 rounded-md shadow-2xl z-50 py-1 max-h-64 overflow-y-auto">
                <div className="px-2 py-1 text-[10px] text-slate-500 uppercase tracking-wider">Synthetic Instruments</div>
                {symbols.map((s) => (
                  <button
                    key={s.id}
                    onClick={() => {
                      setSymbol(s.id);
                      setSymbolMenuOpen(false);
                    }}
                    className={`w-full text-left px-3 py-1.5 hover:bg-cyan-950/60 flex items-center justify-between transition-colors ${
                      s.id === activeSymbol ? 'bg-cyan-950 text-cyan-400 font-bold' : 'text-slate-200'
                    }`}
                  >
                    <span>{s.symbol}</span>
                    <span className="text-[10px] text-slate-500">{s.type.toUpperCase()}</span>
                  </button>
                ))}
              </div>
            )}
          </div>

          <span className="text-slate-700">|</span>

          {/* Timeframe Selector */}
          <div className="flex items-center space-x-1">
            {timeframes.map((tf) => (
              <button
                key={tf.id}
                onClick={() => setTimeframe(tf.goatApiTimeframe)}
                className={`px-2 py-0.5 rounded text-xs transition-colors ${
                  activeTimeframe === tf.goatApiTimeframe
                    ? 'bg-cyan-500 text-slate-950 font-bold'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                }`}
              >
                {tf.label}
              </button>
            ))}
          </div>

          <span className="text-slate-700">|</span>

          {/* Chart Style Selector */}
          <div className="flex items-center space-x-1 bg-slate-900 p-0.5 rounded border border-slate-800">
            <button
              onClick={() => setChartStyle('candlestick')}
              title="Candlesticks"
              className={`p-1 rounded ${chartStyle === 'candlestick' ? 'bg-slate-700 text-cyan-400' : 'text-slate-400 hover:text-slate-200'}`}
            >
              <BarChart2 className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => setChartStyle('line')}
              title="Line Chart"
              className={`p-1 rounded ${chartStyle === 'line' ? 'bg-slate-700 text-cyan-400' : 'text-slate-400 hover:text-slate-200'}`}
            >
              <TrendingUp className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => setChartStyle('area')}
              title="Area Chart"
              className={`p-1 rounded ${chartStyle === 'area' ? 'bg-slate-700 text-cyan-400' : 'text-slate-400 hover:text-slate-200'}`}
            >
              <Activity className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Right Toolbar Controls */}
        <div className="flex items-center space-x-2">
          {/* Grid Layout Selector */}
          <div className="flex items-center space-x-1 bg-slate-900 p-0.5 rounded border border-slate-800">
            <button
              onClick={() => setLayoutMode('single')}
              title="Single Chart"
              className={`p-1 rounded ${layoutMode === 'single' ? 'bg-slate-700 text-cyan-400' : 'text-slate-400 hover:text-slate-200'}`}
            >
              <Square className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => setLayoutMode('split_h')}
              title="Horizontal Split"
              className={`p-1 rounded ${layoutMode === 'split_h' ? 'bg-slate-700 text-cyan-400' : 'text-slate-400 hover:text-slate-200'}`}
            >
              <Layers className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => setLayoutMode('grid_2x2')}
              title="2x2 Grid"
              className={`p-1 rounded ${layoutMode === 'grid_2x2' ? 'bg-slate-700 text-cyan-400' : 'text-slate-400 hover:text-slate-200'}`}
            >
              <Grid className="w-3.5 h-3.5" />
            </button>
          </div>

          <span className="text-slate-700">|</span>

          {/* Replay Toggle Standby */}
          <button
            onClick={toggleReplayMode}
            className={`flex items-center space-x-1 px-2 py-0.5 rounded border text-[11px] font-semibold transition-colors ${
              isReplayMode ? 'bg-amber-950 text-amber-400 border-amber-800' : 'bg-slate-900 text-slate-400 border-slate-800 hover:text-slate-200'
            }`}
          >
            <RotateCcw className="w-3 h-3" />
            <span>REPLAY</span>
          </button>

          {/* Fullscreen */}
          <button
            onClick={toggleFullscreen}
            className="p-1 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded transition-colors"
            title="Toggle Fullscreen"
          >
            <Maximize2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Main Container Area (Left Drawing Toolbar + Canvas Grid) */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Drawing Tools Sidebar */}
        <div className="w-10 bg-[#090d16] border-r border-slate-800 flex flex-col items-center py-2 space-y-2 z-10">
          <button
            onClick={() => handleToolSelect('cursor')}
            title="Cursor / Select"
            className={`p-1.5 rounded transition-colors ${activeTool === 'cursor' ? 'bg-cyan-500/20 text-cyan-400' : 'text-slate-400 hover:text-slate-200'}`}
          >
            <MousePointer className="w-4 h-4" />
          </button>
          <button
            onClick={() => handleToolSelect('trendline')}
            title="Trendline"
            className={`p-1.5 rounded transition-colors ${activeTool === 'trendline' ? 'bg-cyan-500/20 text-cyan-400' : 'text-slate-400 hover:text-slate-200'}`}
          >
            <MoveUpRight className="w-4 h-4" />
          </button>
          <button
            onClick={() => handleToolSelect('horizontal_line')}
            title="Horizontal Line"
            className={`p-1.5 rounded transition-colors ${activeTool === 'horizontal_line' ? 'bg-cyan-500/20 text-cyan-400' : 'text-slate-400 hover:text-slate-200'}`}
          >
            <Minus className="w-4 h-4" />
          </button>
          <button
            onClick={() => handleToolSelect('rectangle')}
            title="Rectangle"
            className={`p-1.5 rounded transition-colors ${activeTool === 'rectangle' ? 'bg-cyan-500/20 text-cyan-400' : 'text-slate-400 hover:text-slate-200'}`}
          >
            <Square className="w-4 h-4" />
          </button>
          <button
            onClick={() => handleToolSelect('ellipse')}
            title="Ellipse / Circle"
            className={`p-1.5 rounded transition-colors ${activeTool === 'ellipse' ? 'bg-cyan-500/20 text-cyan-400' : 'text-slate-400 hover:text-slate-200'}`}
          >
            <Circle className="w-4 h-4" />
          </button>
          <button
            onClick={() => handleToolSelect('text')}
            title="Text Label"
            className={`p-1.5 rounded transition-colors ${activeTool === 'text' ? 'bg-cyan-500/20 text-cyan-400' : 'text-slate-400 hover:text-slate-200'}`}
          >
            <Type className="w-4 h-4" />
          </button>
          <button
            onClick={() => handleToolSelect('measure')}
            title="Measure Tool"
            className={`p-1.5 rounded transition-colors ${activeTool === 'measure' ? 'bg-cyan-500/20 text-cyan-400' : 'text-slate-400 hover:text-slate-200'}`}
          >
            <Ruler className="w-4 h-4" />
          </button>

          <div className="w-6 h-px bg-slate-800 my-1" />

          <button
            onClick={handleMagnetToggle}
            title="Magnet Mode"
            className={`p-1.5 rounded transition-colors ${isMagnet ? 'bg-amber-500/20 text-amber-400' : 'text-slate-400 hover:text-slate-200'}`}
          >
            <Magnet className="w-4 h-4" />
          </button>
          <button
            onClick={handleClearDrawings}
            title="Clear All Drawings"
            className="p-1.5 text-slate-400 hover:text-rose-400 rounded transition-colors"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>

        {/* Canvas Panel Grid Area */}
        <div
          className={`flex-1 grid gap-1 p-1 bg-[#04060a] ${
            layoutMode === 'split_h'
              ? 'grid-cols-2 grid-rows-1'
              : layoutMode === 'split_v'
              ? 'grid-cols-1 grid-rows-2'
              : layoutMode === 'grid_2x2'
              ? 'grid-cols-2 grid-rows-2'
              : 'grid-cols-1 grid-rows-1'
          }`}
        >
          {panels.map((p) => (
            <TradingViewWidget
              key={p.id}
              panelId={p.id}
              symbol={p.symbol}
              timeframe={p.timeframe}
              chartStyle={chartStyle}
              activeTool={activeTool}
              theme={theme}
              showVolume={showVolume}
              showGridLines={showGridLines}
            />
          ))}
        </div>
      </div>
    </div>
  );
};
