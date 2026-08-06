/**
 * Project GOAT v1.0 — Research Hypotheses Workspace
 */

import React, { useState } from 'react';
import { usePipelineStore } from '../stores/pipelineStore';
import { TradingViewContainer } from '../charting/TradingViewContainer';

export const ResearchPage: React.FC = () => {
  const { inspectEntityById } = usePipelineStore();
  const [selectedSymbol, setSelectedSymbol] = useState('VOLATILITY_10');

  const hypotheses = [
    { id: 'HYP_VOL10_001', name: 'Volatility 10 Microstructure Momentum', symbol: 'VOLATILITY_10', status: 'VALIDATING', score: 0.94, author: 'QUANT_RESEARCHER' },
    { id: 'HYP_BOOM500_002', name: 'Boom 500 Spike Reversion Anomaly', symbol: 'BOOM_500', status: 'APPROVED', score: 0.98, author: 'QUANT_RESEARCHER' },
    { id: 'HYP_CRASH1000_003', name: 'Crash 1000 Volatility Spike Switching', symbol: 'CRASH_1000', status: 'EVALUATING', score: 0.88, author: 'SYSTEM_OPERATOR' },
  ];

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center space-x-2">
            <span>🔬</span>
            <span>RESEARCH HYPOTHESES WORKSPACE</span>
          </h1>
          <p className="text-xs text-slate-400">
            Formulate, inspect, and manage mathematical alpha hypotheses across synthetic indices.
          </p>
        </div>
        <span className="text-xs font-mono text-cyan-400 bg-slate-900 border border-cyan-900 px-3 py-1 rounded">
          Active Hypotheses: {hypotheses.length}
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {hypotheses.map((item) => (
          <div
            key={item.id}
            onClick={() => {
              setSelectedSymbol(item.symbol);
              inspectEntityById(item.id);
            }}
            className={`p-4 bg-slate-900 border ${
              selectedSymbol === item.symbol ? 'border-cyan-500 bg-slate-900/90' : 'border-slate-800 hover:border-cyan-500'
            } rounded-lg cursor-pointer transition-all space-y-3`}
          >
            <div className="flex justify-between items-center">
              <span className="text-xs font-mono font-bold text-cyan-300">{item.id}</span>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800">
                {item.status}
              </span>
            </div>

            <div className="text-sm font-semibold text-slate-100">{item.name}</div>

            <div className="flex justify-between text-xs font-mono text-slate-400 pt-2 border-t border-slate-800">
              <span>Symbol: {item.symbol}</span>
              <span>Score: {item.score}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Embedded Hypothesis Interactive TradingView Chart */}
      <div className="bg-[#0b101b] border border-slate-800 p-4 rounded-xl space-y-3">
        <h3 className="text-sm font-bold font-mono text-slate-100">Hypothesis Visual Verification Chart ({selectedSymbol})</h3>
        <TradingViewContainer initialSymbol={selectedSymbol} initialTimeframe="1M" className="h-[480px]" />
      </div>
    </div>
  );
};
