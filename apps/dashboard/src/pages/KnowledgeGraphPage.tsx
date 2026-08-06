/**
 * Project GOAT v1.0 — Knowledge Graph Workspace
 */

import React from 'react';
import { usePipelineStore } from '../stores/pipelineStore';

export const KnowledgeGraphPage: React.FC = () => {
  const { inspectEntityById } = usePipelineStore();

  const nodes = [
    { id: 'KNO_VOL10_001', name: 'Microstructure Momentum Anomaly Node', connections: 4, symbol: 'VOLATILITY_10', status: 'ACTIVE' },
    { id: 'KNO_BOOM500_002', name: 'Spike Reversion Regime Node', connections: 6, symbol: 'BOOM_500', status: 'ACTIVE' },
  ];

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
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {nodes.map((item) => (
          <div
            key={item.id}
            onClick={() => inspectEntityById(item.id)}
            className="p-4 bg-slate-900 border border-slate-800 hover:border-cyan-500 rounded-lg cursor-pointer transition-all space-y-3 font-mono"
          >
            <div className="flex justify-between items-center text-xs">
              <span className="font-bold text-cyan-300">{item.id}</span>
              <span className="px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800 text-[10px]">
                {item.status}
              </span>
            </div>
            <div className="text-sm font-sans font-semibold text-slate-100">{item.name}</div>
            <div className="flex justify-between text-xs text-slate-400 pt-2 border-t border-slate-800">
              <span>Symbol: {item.symbol}</span>
              <span>Connections: {item.connections} Links</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
