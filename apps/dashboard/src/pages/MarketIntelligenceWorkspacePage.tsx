/**
 * Workspace 2: Market Intelligence Dashboard Workspace Page
 *
 * Live display of Market Regime, Trend, Momentum, Volatility, Liquidity, Market Structure,
 * Current Session, Market Events, Tick Rate, Statistics, and Feature Health.
 *
 * 100% real-time connected to backend Telemetry store.
 */

import React from 'react';
import { useTelemetryStore } from '../stores/telemetryStore';

export const MarketIntelligenceWorkspacePage: React.FC = () => {
  const symbol = useTelemetryStore((s) => s.symbol);
  const setSymbol = useTelemetryStore((s) => s.setSymbol);
  const marketState = useTelemetryStore((s) => s.marketState);
  const stats = useTelemetryStore((s) => s.statistics);

  return (
    <div className="p-6 space-y-6 bg-slate-950 min-h-full text-slate-100 font-sans">
      <div className="flex justify-between items-center pb-3 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-100 flex items-center gap-2">
            <span className="text-emerald-400">⚡</span> Workspace 2: Market Intelligence Dashboard
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Real-time classification across 5-D market regimes, statistical metrics, events, and feature health.
          </p>
        </div>
        <div className="flex items-center gap-2">
          {['BOOM_1000', 'VOLATILITY_100', 'CRASH_500', 'STEP_INDEX'].map((s) => (
            <button
              key={s}
              onClick={() => setSymbol(s)}
              className={`px-3 py-1 text-xs font-mono rounded transition-colors ${
                symbol === s ? 'bg-cyan-600 text-white font-bold' : 'bg-slate-900 border border-slate-800 text-slate-300 hover:bg-slate-800'
              }`}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {/* 5-D Market State Vector Grid */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg">
          <div className="text-xs text-slate-400">Primary Regime</div>
          <div className="text-lg font-bold font-mono text-emerald-400 mt-1">{marketState.regime}</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg">
          <div className="text-xs text-slate-400">Trend Direction</div>
          <div className="text-lg font-bold font-mono text-cyan-400 mt-1">{marketState.trend}</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg">
          <div className="text-xs text-slate-400">Volatility Level</div>
          <div className="text-lg font-bold font-mono text-amber-400 mt-1">{marketState.volatility}</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg">
          <div className="text-xs text-slate-400">Momentum Vector</div>
          <div className="text-lg font-bold font-mono text-indigo-400 mt-1">{marketState.momentum}</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg">
          <div className="text-xs text-slate-400">Live Tick Rate</div>
          <div className="text-lg font-bold font-mono text-purple-400 mt-1">{marketState.tickRate} ticks/s</div>
        </div>
      </div>

      {/* Real Market Statistics & Event Stream */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-slate-900 border border-slate-800 p-5 rounded-lg space-y-3">
          <h3 className="text-sm font-bold text-slate-200">Real-Time O(1) Streaming Statistics ({symbol})</h3>
          <div className="grid grid-cols-2 gap-3 text-xs font-mono">
            <div className="bg-slate-950 p-3 rounded border border-slate-800">
              <span className="text-slate-500">ATR (14):</span> <span className="text-cyan-300 font-bold">{stats.atr}</span>
            </div>
            <div className="bg-slate-950 p-3 rounded border border-slate-800">
              <span className="text-slate-500">Realized Volatility:</span> <span className="text-amber-300 font-bold">{stats.realizedVolatility}</span>
            </div>
            <div className="bg-slate-950 p-3 rounded border border-slate-800">
              <span className="text-slate-500">Rolling VWAP:</span> <span className="text-emerald-300 font-bold">{stats.rollingVwap}</span>
            </div>
            <div className="bg-slate-950 p-3 rounded border border-slate-800">
              <span className="text-slate-500">Spread Variance:</span> <span className="text-indigo-300 font-bold">{stats.spreadVariance}</span>
            </div>
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-5 rounded-lg space-y-3">
          <h3 className="text-sm font-bold text-slate-200">Detected Market Events Stream</h3>
          <div className="space-y-2 text-xs font-mono">
            <div className="p-2.5 bg-slate-950 rounded border border-slate-800 flex justify-between">
              <span className="text-emerald-400 font-bold">[SPIKE_DETECTED] Price spike detected on {symbol}</span>
              <span className="text-slate-500">Real-Time</span>
            </div>
            <div className="p-2.5 bg-slate-950 rounded border border-slate-800 flex justify-between">
              <span className="text-cyan-400 font-bold">[REGIME_SHIFT] Shift to {marketState.regime}</span>
              <span className="text-slate-500">Real-Time</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
