/**
 * Workspace 6: Research Timeline Workspace Page
 *
 * Chronological timeline displaying Hypothesis Created, Validated, Rejected, Edge Activated,
 * Edge Degraded, Edge Retired, Research Reports Generated, Session Changes, Market Events.
 */

import React from 'react';

export const ResearchTimelineWorkspacePage: React.FC = () => {
  const events = [
    { id: 'EVT_001', time: '12:00:14 UTC', type: 'EDGE_ACTIVATED', text: 'DiscoveredEdge EDG_00018F42A109C3E1 activated on BOOM_1000', score: '0.92', badge: 'bg-emerald-950 text-emerald-300 border-emerald-800' },
    { id: 'EVT_002', time: '11:58:30 UTC', type: 'REPORT_GENERATED', text: 'ResearchReport REP_0001F82A4B92C3D4 generated for EDG_00018F42A109C3E1', score: 'REP', badge: 'bg-purple-950 text-purple-300 border-purple-800' },
    { id: 'EVT_003', time: '11:55:00 UTC', type: 'HYPOTHESIS_VALIDATED', text: 'Hypothesis HYP_00018F42A109C3E1 passed statistical significance (p=0.008)', score: 'p=0.008', badge: 'bg-cyan-950 text-cyan-300 border-cyan-800' },
    { id: 'EVT_004', time: '11:45:12 UTC', type: 'MARKET_EVENT', text: 'Volatility Expansion event detected on VOLATILITY_100', score: 'EVENT', badge: 'bg-amber-950 text-amber-300 border-amber-800' },
    { id: 'EVT_005', time: '11:30:00 UTC', type: 'EDGE_DEGRADED', text: 'Edge EDG_00046B19D432F6B4 shifted to WATCHLIST due to expectancy drift', score: 'WATCHLIST', badge: 'bg-rose-950 text-rose-300 border-rose-800' },
  ];

  return (
    <div className="p-6 space-y-6 bg-slate-950 min-h-full text-slate-100">
      <div className="flex justify-between items-center pb-3 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-100 flex items-center gap-2">
            <span className="text-cyan-400">📅</span> Workspace 6: Research Timeline
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Chronological audit log tracking hypothesis lifecycle, edge activations, degradations, and reports.
          </p>
        </div>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-lg p-6 space-y-6">
        <div className="relative border-l-2 border-slate-800 ml-4 space-y-6">
          {events.map((e) => (
            <div key={e.id} className="relative pl-6">
              <div className="absolute -left-[9px] top-1.5 w-4 h-4 rounded-full bg-slate-900 border-2 border-cyan-500"></div>
              <div className="bg-slate-950 p-4 rounded-lg border border-slate-800 flex justify-between items-start gap-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono text-slate-500">{e.time}</span>
                    <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded border ${e.badge}`}>{e.type}</span>
                  </div>
                  <div className="text-sm font-semibold text-slate-200">{e.text}</div>
                </div>
                <span className="text-xs font-mono text-slate-400 bg-slate-900 px-2.5 py-1 rounded border border-slate-800">{e.score}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
