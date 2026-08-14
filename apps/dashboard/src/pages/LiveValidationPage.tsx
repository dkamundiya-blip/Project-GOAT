/**
 * Project GOAT v1.0 — Live Validation Workspace
 */

import React from 'react';

import { useTelemetryStore } from '../stores/telemetryStore';

export const LiveValidationPage: React.FC = () => {
  const telemetry = useTelemetryStore();

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center space-x-2">
            <span>⚡</span>
            <span>LIVE VALIDATION SESSIONS WORKSPACE</span>
          </h1>
          <p className="text-xs text-slate-400">
            Real-time paper trading session telemetry, fill latency monitoring, and zero-execution paper testing.
          </p>
        </div>
        <span className="text-xs font-mono text-cyan-400 bg-slate-900 border border-cyan-900 px-3 py-1 rounded">
          Active Sessions: 0
        </span>
      </div>

      <div className="p-8 bg-slate-900/60 border border-dashed border-slate-800 rounded-xl text-center space-y-3">
        <div className="text-2xl">⚡</div>
        <div className="text-sm font-semibold text-slate-200">NO LIVE VALIDATION SESSIONS ACTIVE</div>
        <p className="text-xs text-slate-400 max-w-lg mx-auto">
          Candidate edges must pass statistical significance and walk-forward verification before live paper validation sessions are initiated.
          Currently in Research / Paper Collection mode.
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 max-w-lg mx-auto pt-4 text-left font-mono text-xs">
          <div className="p-3 bg-slate-950 rounded border border-slate-800">
            <span className="text-slate-500 block text-[10px]">DISCOVERED EDGES</span>
            <span className="font-bold text-cyan-300">{telemetry.edges.length}</span>
          </div>
          <div className="p-3 bg-slate-950 rounded border border-slate-800">
            <span className="text-slate-500 block text-[10px]">EXECUTION MODE</span>
            <span className="font-bold text-amber-300">PAPER_ONLY</span>
          </div>
          <div className="p-3 bg-slate-950 rounded border border-slate-800">
            <span className="text-slate-500 block text-[10px]">HOLDOUT ISOLATION</span>
            <span className="font-bold text-emerald-300">ENFORCED</span>
          </div>
        </div>
      </div>
    </div>
  );
};
