/**
 * Workspace 7: Knowledge Graph Explorer Workspace Page
 *
 * Visualizes Features -> Hypotheses -> Edges -> Regimes -> Symbols -> Sessions -> Validation Results.
 * Interactive graph node search, filtering, and detail inspection.
 */

import React, { useState } from 'react';

export const KnowledgeGraphWorkspacePage: React.FC = () => {
  const [selectedFilter, setSelectedFilter] = useState('ALL');
  const [selectedNode, setSelectedNode] = useState<string | null>('EDG_00018F42A109C3E1');

  const nodes = [
    { id: 'EDG_00018F42A109C3E1', label: 'Edge: BOOM_1000 Trend', type: 'EDGE', color: 'bg-emerald-950 border-emerald-500 text-emerald-300' },
    { id: 'HYP_00018F42A109C3E1', label: 'Hypothesis: Trend+ZScore', type: 'HYPOTHESIS', color: 'bg-purple-950 border-purple-500 text-purple-300' },
    { id: 'RKN_TREND_STRENGTH', label: 'Feature: trend_strength', type: 'FEATURE', color: 'bg-cyan-950 border-cyan-500 text-cyan-300' },
    { id: 'RKN_Z_SCORE', label: 'Feature: z_score', type: 'FEATURE', color: 'bg-cyan-950 border-cyan-500 text-cyan-300' },
    { id: 'RKN_HIGH_VOLATILITY', label: 'Regime: HIGH_VOLATILITY', type: 'REGIME', color: 'bg-amber-950 border-amber-500 text-amber-300' },
    { id: 'RKN_BOOM_1000', label: 'Symbol: BOOM_1000', type: 'SYMBOL', color: 'bg-indigo-950 border-indigo-500 text-indigo-300' },
  ];

  const filteredNodes = nodes.filter((n) => selectedFilter === 'ALL' || n.type === selectedFilter);

  return (
    <div className="p-6 space-y-6 bg-slate-950 min-h-full text-slate-100">
      <div className="flex justify-between items-center pb-3 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-100 flex items-center gap-2">
            <span className="text-cyan-400">🕸️</span> Workspace 7: Knowledge Graph Explorer
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Interactive research graph mapping features, hypotheses, edges, regimes, and symbol relationships.
          </p>
        </div>
      </div>

      {/* Graph Filter Bar */}
      <div className="flex items-center gap-2 bg-slate-900 border border-slate-800 p-3 rounded-lg text-xs font-mono">
        <span className="text-slate-400 mr-2">Filter Node Type:</span>
        {['ALL', 'EDGE', 'HYPOTHESIS', 'FEATURE', 'REGIME', 'SYMBOL'].map((t) => (
          <button
            key={t}
            onClick={() => setSelectedFilter(t)}
            className={`px-3 py-1 rounded transition-colors ${
              selectedFilter === t ? 'bg-cyan-600 text-white font-bold' : 'bg-slate-800 text-slate-400 hover:text-slate-200'
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {/* Graph Visualization Container */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2 bg-slate-900 border border-slate-800 p-6 rounded-lg min-h-[400px] flex flex-wrap items-center justify-center gap-4 relative overflow-hidden">
          <div className="absolute top-3 left-3 text-xs font-mono text-slate-500">Interactive DAG Graph Layout (Zoom: 100%)</div>

          {filteredNodes.map((n) => (
            <div
              key={n.id}
              onClick={() => setSelectedNode(n.id)}
              className={`p-4 rounded-xl border-2 cursor-pointer shadow-lg transition-transform hover:scale-105 ${n.color} ${
                selectedNode === n.id ? 'ring-2 ring-cyan-400 font-bold scale-105' : ''
              }`}
            >
              <div className="text-[10px] font-mono opacity-70">{n.type}</div>
              <div className="text-xs font-mono font-bold mt-1">{n.label}</div>
              <div className="text-[10px] font-mono text-slate-400 mt-2">{n.id}</div>
            </div>
          ))}
        </div>

        {/* Selected Node Inspector */}
        <div className="bg-slate-900 border border-slate-800 p-5 rounded-lg space-y-4 font-mono text-xs">
          <h3 className="text-sm font-bold text-slate-200 border-b border-slate-800 pb-2">Graph Node Details</h3>
          {selectedNode ? (
            <div className="space-y-3">
              <div>
                <span className="text-slate-500 text-[10px]">Node Identifier</span>
                <div className="text-cyan-300 font-bold">{selectedNode}</div>
              </div>
              <div>
                <span className="text-slate-500 text-[10px]">Degree Connections</span>
                <div className="text-slate-200">Incoming: 2 | Outgoing: 4</div>
              </div>
              <div>
                <span className="text-slate-500 text-[10px]">Canonical Hash</span>
                <div className="text-slate-400 break-all text-[11px]">8F42A109C3E1B9E2D314C5F60001</div>
              </div>
            </div>
          ) : (
            <div className="text-slate-500">Click a node to inspect relationships.</div>
          )}
        </div>
      </div>
    </div>
  );
};
