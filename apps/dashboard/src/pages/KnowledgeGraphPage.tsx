/**
 * Project GOAT v1.0 — Knowledge Graph Workspace
 */

import React from 'react';

import { useTelemetryStore } from '../stores/telemetryStore';

export const KnowledgeGraphPage: React.FC = () => {
  const telemetry = useTelemetryStore();

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center space-x-2">
            <span>🕸️</span>
            <span>KNOWLEDGE GRAPH WORKSPACE</span>
          </h1>
          <p className="text-xs text-slate-400">
            Semantic node graph linking synthetic index market regimes, anomaly patterns, and edge candidate lineage.
          </p>
        </div>
        <span className="text-xs font-mono text-cyan-400 bg-slate-900 border border-cyan-900 px-3 py-1 rounded">
          Active Nodes: {telemetry.edges.length}
        </span>
      </div>

      {telemetry.edges.length === 0 ? (
        <div className="p-8 bg-slate-900/60 border border-dashed border-slate-800 rounded-xl text-center space-y-3">
          <div className="text-2xl">🕸️</div>
          <div className="text-sm font-semibold text-slate-200">NO KNOWLEDGE GRAPH NODES POPULATED YET</div>
          <p className="text-xs text-slate-400 max-w-lg mx-auto">
            Semantic nodes link discovered statistical edges with market regimes and feature patterns.
            Nodes will populate as candidate edges pass qualification.
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-md mx-auto pt-4 text-left font-mono text-xs">
            <div className="p-3 bg-slate-950 rounded border border-slate-800">
              <span className="text-slate-500 block text-[10px]">GRAPH PERSISTENCE</span>
              <span className="font-bold text-cyan-300">SQLite / knowledge_graph</span>
            </div>
            <div className="p-3 bg-slate-950 rounded border border-slate-800">
              <span className="text-slate-500 block text-[10px]">LINEAGE VERIFICATION</span>
              <span className="font-bold text-emerald-300">DETERMINISTIC_SHA256</span>
            </div>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {telemetry.edges.map((edge) => (
            <div
              key={edge.id}
              className="p-4 bg-slate-900 border border-slate-800 rounded-lg space-y-3 font-mono"
            >
              <div className="flex justify-between items-center text-xs">
                <span className="font-bold text-cyan-300">KNO_{edge.id}</span>
                <span className="px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800 text-[10px]">
                  {edge.status}
                </span>
              </div>
              <div className="text-sm font-sans font-semibold text-slate-100">{edge.symbol} Knowledge Node</div>
              <div className="flex justify-between text-xs text-slate-400 pt-2 border-t border-slate-800">
                <span>Features: {edge.features}</span>
                <span>Score: {edge.score}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
