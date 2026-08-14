/**
 * Project GOAT v1.0 — Research Intelligence Workspace
 */

import React from 'react';

import { useTelemetryStore } from '../stores/telemetryStore';

export const ResearchIntelligencePage: React.FC = () => {
  const telemetry = useTelemetryStore();

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center space-x-2">
            <span>💡</span>
            <span>RESEARCH INTELLIGENCE WORKSPACE</span>
          </h1>
          <p className="text-xs text-slate-400">
            Institutional research insights, cross-dataset correlation matrices, and alpha decay forecasts.
          </p>
        </div>
        <span className="text-xs font-mono text-cyan-400 bg-slate-900 border border-cyan-900 px-3 py-1 rounded">
          Intelligence Score: {telemetry.edges.length > 0 ? 'ACTIVE' : 'N/A'}
        </span>
      </div>

      <div className="p-8 bg-slate-900/60 border border-dashed border-slate-800 rounded-xl text-center space-y-3">
        <div className="text-2xl">💡</div>
        <div className="text-sm font-semibold text-slate-200">NO SYNTHESIZED RESEARCH INTELLIGENCE REPORTS YET</div>
        <p className="text-xs text-slate-400 max-w-lg mx-auto">
          The Research Intelligence Engine generates meta-analysis correlation matrices and alpha decay forecasts
          after multiple candidate edges are validated and promoted.
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 max-w-lg mx-auto pt-4 text-left font-mono text-xs">
          <div className="p-3 bg-slate-950 rounded border border-slate-800">
            <span className="text-slate-500 block text-[10px]">MARKET REGIME</span>
            <span className="font-bold text-cyan-300">{telemetry.marketState.regime}</span>
          </div>
          <div className="p-3 bg-slate-950 rounded border border-slate-800">
            <span className="text-slate-500 block text-[10px]">CURRENT TREND</span>
            <span className="font-bold text-emerald-300">{telemetry.marketState.trend}</span>
          </div>
          <div className="p-3 bg-slate-950 rounded border border-slate-800">
            <span className="text-slate-500 block text-[10px]">ALPHA DECAY MODELS</span>
            <span className="font-bold text-purple-300">ONLINE</span>
          </div>
        </div>
      </div>
    </div>
  );
};
