/**
 * Project GOAT v1.0 — Experiments Workspace
 */

import React from 'react';

import { useTelemetryStore } from '../stores/telemetryStore';

export const ExperimentsPage: React.FC = () => {
  const telemetry = useTelemetryStore();

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center space-x-2">
            <span>🧪</span>
            <span>EXPERIMENT ENGINE WORKSPACE</span>
          </h1>
          <p className="text-xs text-slate-400">
            Out-of-sample cross validation, noise perturbation matrix, and robustness testing.
          </p>
        </div>
        <span className="text-xs font-mono text-cyan-400 bg-slate-900 border border-cyan-900 px-3 py-1 rounded">
          Closed Windows: {telemetry.candlesClosed}
        </span>
      </div>

      <div className="p-8 bg-slate-900/60 border border-dashed border-slate-800 rounded-xl text-center space-y-3">
        <div className="text-2xl">🧪</div>
        <div className="text-sm font-semibold text-slate-200">
          {telemetry.candlesClosed > 0
            ? 'CANDLE EXPERIMENT WINDOWS ACTIVE'
            : 'WARMING UP — NO EXPERIMENT SESSIONS RUN YET'}
        </div>
        <p className="text-xs text-slate-400 max-w-lg mx-auto">
          Deterministic experiment runs and out-of-sample cross validations are triggered when candidate hypotheses meet significance thresholds.
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 max-w-lg mx-auto pt-4 text-left font-mono text-xs">
          <div className="p-3 bg-slate-950 rounded border border-slate-800">
            <span className="text-slate-500 block text-[10px]">EVALUATED EDGES</span>
            <span className="font-bold text-cyan-300">{telemetry.edgesEvaluated}</span>
          </div>
          <div className="p-3 bg-slate-950 rounded border border-slate-800">
            <span className="text-slate-500 block text-[10px]">CANDLE WINDOWS</span>
            <span className="font-bold text-emerald-300">{telemetry.candlesClosed}</span>
          </div>
          <div className="p-3 bg-slate-950 rounded border border-slate-800">
            <span className="text-slate-500 block text-[10px]">PIPELINE LATENCY</span>
            <span className="font-bold text-purple-300">{telemetry.pipelineLatencyMs.toFixed(2)} ms</span>
          </div>
        </div>
      </div>
    </div>
  );
};
