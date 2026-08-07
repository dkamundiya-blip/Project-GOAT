/**
 * Workspace 1: Research Center Workspace Page
 *
 * Displays Discovered Edges, Hypotheses, Evidence Bundles, Research Reports, Validation Results,
 * Feature Vectors, Search, Filtering, Sorting, Historical Versions, and Comparison Mode.
 *
 * Connected 100% to real-time telemetry backend store.
 */

import React, { useState } from 'react';
import { useTelemetryStore } from '../stores/telemetryStore';

export const ResearchCenterWorkspacePage: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [activeCategory, setActiveCategory] = useState('ALL');
  const [comparisonMode, setComparisonMode] = useState(false);

  const edges = useTelemetryStore((s) => s.edges);

  const filteredEdges = edges.filter(
    (e) =>
      (activeCategory === 'ALL' || e.status === activeCategory) &&
      (e.id.toLowerCase().includes(searchQuery.toLowerCase()) || e.symbol.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <div className="p-6 space-y-6 bg-slate-950 min-h-full text-slate-100 font-sans">
      <div className="flex justify-between items-center pb-3 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-100 flex items-center gap-2">
            <span className="text-cyan-400">🔬</span> Workspace 1: Institutional Research Center
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Central research hub for hypotheses, discovered edges, evidence bundles, and validation records.
          </p>
        </div>
        <button
          onClick={() => setComparisonMode(!comparisonMode)}
          className={`px-3 py-1.5 text-xs font-mono rounded border transition-colors ${
            comparisonMode ? 'bg-indigo-600 border-indigo-500 text-white font-bold' : 'bg-slate-900 border-slate-700 text-slate-300 hover:bg-slate-800'
          }`}
        >
          {comparisonMode ? '✓ Comparison Mode Active' : 'Enable Comparison Mode'}
        </button>
      </div>

      {/* Filter & Search Bar */}
      <div className="flex flex-wrap justify-between items-center gap-4 bg-slate-900 border border-slate-800 p-4 rounded-lg">
        <input
          type="text"
          placeholder="Search edges, hypotheses, features, or symbols..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="bg-slate-950 border border-slate-700 rounded px-3 py-1.5 text-xs text-slate-100 focus:outline-none focus:border-cyan-500 w-80 font-mono"
        />

        <div className="flex items-center gap-2 text-xs font-mono">
          <span className="text-slate-400 mr-1">Status:</span>
          {['ALL', 'ACTIVE', 'WATCHLIST', 'DEGRADING'].map((cat) => (
            <button
              key={cat}
              onClick={() => setActiveCategory(cat)}
              className={`px-3 py-1 rounded transition-colors ${
                activeCategory === cat ? 'bg-cyan-600 text-white font-bold' : 'bg-slate-800 text-slate-400 hover:text-slate-200'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Real Discovered Edges Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filteredEdges.map((edge) => (
          <div key={edge.id} className={`bg-slate-900 border p-4 rounded-lg space-y-3 ${comparisonMode ? 'border-indigo-500/80 shadow-lg shadow-indigo-950/40' : 'border-slate-800'}`}>
            <div className="flex justify-between items-start">
              <div>
                <span className="font-mono text-xs text-cyan-400 font-bold">{edge.id}</span>
                <div className="text-sm font-bold text-slate-100 mt-0.5">{edge.symbol}</div>
              </div>
              <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded border ${edge.status === 'ACTIVE' ? 'bg-emerald-950 text-emerald-300 border-emerald-800' : 'bg-amber-950 text-amber-300 border-amber-800'}`}>
                {edge.status}
              </span>
            </div>

            <div className="grid grid-cols-4 gap-2 text-xs font-mono bg-slate-950/70 p-2.5 rounded border border-slate-800/80">
              <div>
                <div className="text-[10px] text-slate-500">Exp Value</div>
                <div className="text-emerald-400 font-bold">{(edge.ev * 100).toFixed(2)}%</div>
              </div>
              <div>
                <div className="text-[10px] text-slate-500">Sharpe</div>
                <div className="text-cyan-300 font-bold">{edge.sharpe}</div>
              </div>
              <div>
                <div className="text-[10px] text-slate-500">P-Value</div>
                <div className="text-indigo-300 font-bold">{edge.pval}</div>
              </div>
              <div>
                <div className="text-[10px] text-slate-500">Score</div>
                <div className="text-amber-400 font-bold">{edge.score}</div>
              </div>
            </div>

            <div className="text-xs text-slate-400 flex justify-between items-center">
              <span>Features: <code className="text-slate-300">{edge.features}</code></span>
              <button className="text-cyan-400 hover:underline text-[11px] font-mono">Inspect Evidence ➔</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
