/**
 * Project GOAT v1.0 — Evidence Collections Workspace
 */

import React from 'react';

import { useTelemetryStore } from '../stores/telemetryStore';

export const EvidencePage: React.FC = () => {
  const telemetry = useTelemetryStore();

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center space-x-2">
            <span>📑</span>
            <span>EVIDENCE COLLECTIONS WORKSPACE</span>
          </h1>
          <p className="text-xs text-slate-400">
            Empirical tick datasets, stationarity metrics, and statistical sample records.
          </p>
        </div>
        <span className="text-xs font-mono text-cyan-400 bg-slate-900 border border-cyan-900 px-3 py-1 rounded">
          Observation Buffer: {telemetry.candlesClosed} / 15 Target
        </span>
      </div>

      <div className="p-8 bg-slate-900/60 border border-dashed border-slate-800 rounded-xl text-center space-y-3">
        <div className="text-2xl">📑</div>
        <div className="text-sm font-semibold text-slate-200">
          {telemetry.candlesClosed >= 15
            ? 'EMPIRICAL OBSERVATION BUFFER ACTIVE'
            : 'WARMING UP — ACCUMULATING EMPIRICAL OBSERVATIONS'}
        </div>
        <p className="text-xs text-slate-400 max-w-lg mx-auto">
          The Evidence Engine pairs candle-close feature vectors with subsequent forward returns.
          A minimum of 15 observation pairs is required before statistical significance testing begins.
        </p>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 max-w-xl mx-auto pt-4 text-left font-mono text-xs">
          <div className="p-3 bg-slate-950 rounded border border-slate-800">
            <span className="text-slate-500 block text-[10px]">TOTAL TICKS</span>
            <span className="font-bold text-cyan-300">{telemetry.ticksProcessed}</span>
          </div>
          <div className="p-3 bg-slate-950 rounded border border-slate-800">
            <span className="text-slate-500 block text-[10px]">CLOSED CANDLES</span>
            <span className="font-bold text-emerald-300">{telemetry.candlesClosed}</span>
          </div>
          <div className="p-3 bg-slate-950 rounded border border-slate-800">
            <span className="text-slate-500 block text-[10px]">FEATURE VECTORS</span>
            <span className="font-bold text-purple-300">{telemetry.featureVectorsGenerated}</span>
          </div>
          <div className="p-3 bg-slate-950 rounded border border-slate-800">
            <span className="text-slate-500 block text-[10px]">ACTIVE EDGES</span>
            <span className="font-bold text-amber-300">{telemetry.edges.length}</span>
          </div>
        </div>
      </div>
    </div>
  );
};
