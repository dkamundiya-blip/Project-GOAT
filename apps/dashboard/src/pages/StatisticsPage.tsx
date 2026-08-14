/**
 * Project GOAT v1.0 — Statistical Evaluation Workspace
 */

import React from 'react';

import { useTelemetryStore } from '../stores/telemetryStore';

export const StatisticsPage: React.FC = () => {
  const telemetry = useTelemetryStore();

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center space-x-2">
            <span>📈</span>
            <span>STATISTICAL EVALUATOR WORKSPACE</span>
          </h1>
          <p className="text-xs text-slate-400">
            Rigorous statistical significance evaluation, continuous market statistics, and t-statistics.
          </p>
        </div>
        <span className="text-xs font-mono text-cyan-400 bg-slate-900 border border-cyan-900 px-3 py-1 rounded">
          Feature Vectors: {telemetry.featureVectorsGenerated}
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-4 bg-slate-900 border border-slate-800 rounded-lg space-y-2 font-mono">
          <div className="text-xs text-slate-400">AVERAGE TRUE RANGE (ATR-14)</div>
          <div className="text-xl font-bold text-cyan-300">
            {telemetry.statistics.atr > 0 ? telemetry.statistics.atr.toFixed(4) : '0.0000'}
          </div>
          <div className="text-[10px] text-slate-500">Source: Market Intelligence Statistics</div>
        </div>

        <div className="p-4 bg-slate-900 border border-slate-800 rounded-lg space-y-2 font-mono">
          <div className="text-xs text-slate-400">REALIZED VOLATILITY (20-BAR)</div>
          <div className="text-xl font-bold text-emerald-300">
            {telemetry.statistics.realizedVolatility > 0 ? telemetry.statistics.realizedVolatility.toFixed(4) : '0.0000'}
          </div>
          <div className="text-[10px] text-slate-500">Source: Market Intelligence Statistics</div>
        </div>

        <div className="p-4 bg-slate-900 border border-slate-800 rounded-lg space-y-2 font-mono">
          <div className="text-xs text-slate-400">ROLLING VWAP</div>
          <div className="text-xl font-bold text-purple-300">
            {telemetry.statistics.rollingVwap > 0 ? telemetry.statistics.rollingVwap.toFixed(2) : '0.00'}
          </div>
          <div className="text-[10px] text-slate-500">Source: Market Intelligence Statistics</div>
        </div>

        <div className="p-4 bg-slate-900 border border-slate-800 rounded-lg space-y-2 font-mono">
          <div className="text-xs text-slate-400">SPREAD VARIANCE</div>
          <div className="text-xl font-bold text-amber-300">
            {telemetry.statistics.spreadVariance > 0 ? telemetry.statistics.spreadVariance.toFixed(4) : '0.0000'}
          </div>
          <div className="text-[10px] text-slate-500">Source: Market Intelligence Statistics</div>
        </div>
      </div>

      {telemetry.edges.length === 0 ? (
        <div className="p-8 bg-slate-900/60 border border-dashed border-slate-800 rounded-xl text-center space-y-3">
          <div className="text-2xl">📈</div>
          <div className="text-sm font-semibold text-slate-200">NO HYPOTHESIS EVALUATIONS PERSISTED YET</div>
          <p className="text-xs text-slate-400 max-w-md mx-auto">
            Statistical hypothesis evaluations (Sharpe, p-values, t-stats) will populate when candidates undergo significance screening.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {telemetry.edges.map((edge) => (
            <div
              key={edge.id}
              className="p-4 bg-slate-900 border border-slate-800 rounded-lg space-y-3 font-mono"
            >
              <div className="flex justify-between items-center text-xs">
                <span className="font-bold text-cyan-300">{edge.id}</span>
                <span className="px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800 text-[10px]">
                  {edge.status}
                </span>
              </div>
              <div className="text-sm font-sans font-semibold text-slate-100">{edge.symbol} Discovered Alpha Edge</div>
              <div className="flex justify-between text-xs text-slate-400 pt-2 border-t border-slate-800">
                <span>Sharpe: {edge.sharpe}</span>
                <span>p-val: {edge.pval}</span>
                <span>EV: +{(edge.ev * 100).toFixed(2)}%</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
