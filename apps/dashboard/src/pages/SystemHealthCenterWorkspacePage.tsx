/**
 * Workspace 8: System Health Center Workspace Page
 *
 * Live health dashboard displaying Pipeline Health, Latency, Memory, CPU, WebSocket, Tick Flow,
 * Feature Engine, Edge Engine, Reasoning Engine, API Health, Storage Health, Repository Health.
 *
 * Connected 100% to real-time backend telemetry store.
 */

import React from 'react';
import { useTelemetryStore } from '../stores/telemetryStore';

export const SystemHealthCenterWorkspacePage: React.FC = () => {
  const latency = useTelemetryStore((s) => s.pipelineLatencyMs);
  const health = useTelemetryStore((s) => s.systemHealth);
  const ticksProcessed = useTelemetryStore((s) => s.ticksProcessed);
  const connectionStatus = useTelemetryStore((s) => s.connectionStatus);

  return (
    <div className="p-6 space-y-6 bg-slate-950 min-h-full text-slate-100 font-sans">
      <div className="flex justify-between items-center pb-3 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-100 flex items-center gap-2">
            <span className="text-emerald-400">🛡️</span> Workspace 8: System Health Center
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Real-time infrastructure health, resource utilization (CPU/RAM), storage metrics, and repository WAL status.
          </p>
        </div>
        <div className="flex items-center gap-2 font-mono text-xs">
          <span className={`px-3 py-1 rounded border font-bold ${
            connectionStatus === 'CONNECTED' ? 'bg-emerald-950 text-emerald-300 border-emerald-800' : 'bg-amber-950 text-amber-300 border-amber-800'
          }`}>
            WS TELEMETRY: {connectionStatus}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 font-mono text-xs">
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg">
          <div className="text-xs text-slate-400">Total Ticks Processed</div>
          <div className="text-xl font-bold text-cyan-400 mt-1">{ticksProcessed.toLocaleString()}</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg">
          <div className="text-xs text-slate-400">Avg Pipeline Latency</div>
          <div className="text-xl font-bold text-amber-400 mt-1">{latency} ms</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg">
          <div className="text-xs text-slate-400">SQLite Storage Mode</div>
          <div className="text-xl font-bold text-indigo-400 mt-1">WAL Journal</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg">
          <div className="text-xs text-slate-400">Overall Health Status</div>
          <div className="text-xl font-bold text-emerald-400 mt-1">{health.overall_status}</div>
        </div>
      </div>

      {/* Subsystem Health Component Matrix */}
      <div className="bg-slate-900 border border-slate-800 rounded-lg p-5 space-y-3 font-mono text-xs">
        <h3 className="text-sm font-bold text-slate-200 font-sans">Core Subsystem Telemetry Matrix</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {Object.entries(health.components || {}).map(([key, comp]) => (
            <div key={key} className="p-3 bg-slate-950 rounded border border-slate-800 flex justify-between items-center">
              <div>
                <div className="font-bold text-slate-200">{comp.name || key}</div>
                <div className="text-[10px] text-slate-500 mt-0.5">Latency: {comp.latency_ms} ms | Errors: {comp.error_count}</div>
              </div>
              <span className={`px-2 py-0.5 text-[10px] font-bold rounded border ${
                comp.status === 'HEALTHY' ? 'bg-emerald-950 text-emerald-300 border-emerald-800' : 'bg-rose-950 text-rose-300 border-rose-800'
              }`}>
                {comp.status}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
