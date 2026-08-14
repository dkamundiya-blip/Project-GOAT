/**
 * Project GOAT v1.0 — Research Hypotheses Workspace
 */

import React, { useState } from 'react';
import { usePipelineStore } from '../stores/pipelineStore';
import { useDashboardStore } from '../stores/dashboardStore';
import { useTelemetryStore } from '../stores/telemetryStore';
import { TradingViewContainer } from '../charting/TradingViewContainer';

export const ResearchPage: React.FC = () => {
  const { inspectEntityById } = usePipelineStore();
  const hypotheses = useDashboardStore((state) => state.hypotheses);
  const telemetry = useTelemetryStore();
  const [selectedSymbol, setSelectedSymbol] = useState<string>(telemetry.symbol || 'BOOM_1000');

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

      {hypotheses.length === 0 ? (
        <div className="p-8 bg-slate-900/60 border border-dashed border-slate-800 rounded-xl text-center space-y-3">
          <div className="text-2xl">🔬</div>
          <div className="text-sm font-semibold text-slate-200">WARMING UP — NO FORMAL HYPOTHESES EVALUATED YET</div>
          <p className="text-xs text-slate-400 max-w-md mx-auto">
            The Hypothesis Engine generates candidate feature combinations after sufficient multi-tick candles close (N &ge; 15).
            Currently observed: {telemetry.candlesClosed} candles closed, {telemetry.ticksProcessed} ticks ingested.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {hypotheses.map((item) => (
            <div
              key={item.hypothesis_id}
              onClick={() => {
                setSelectedSymbol(telemetry.symbol || 'BOOM_1000');
                inspectEntityById(item.hypothesis_id);
              }}
              className="p-4 bg-slate-900 border border-slate-800 hover:border-cyan-500 rounded-lg cursor-pointer transition-all space-y-3"
            >
              <div className="flex justify-between items-center">
                <span className="text-xs font-mono font-bold text-cyan-300">{item.hypothesis_id}</span>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800">
                  {item.status}
                </span>
              </div>
              <div className="text-sm font-semibold text-slate-100">{item.title}</div>
              <div className="flex justify-between text-xs font-mono text-slate-400 pt-2 border-t border-slate-800">
                <span>Category: {item.category}</span>
                <span>Conf: {item.confidence_score}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Embedded Hypothesis Interactive TradingView Chart */}
      <div className="bg-[#0b101b] border border-slate-800 p-4 rounded-xl space-y-3">
        <h3 className="text-sm font-bold font-mono text-slate-100">Hypothesis Visual Verification Chart ({selectedSymbol})</h3>
        <TradingViewContainer initialSymbol={selectedSymbol} initialTimeframe="1M" className="h-[480px]" />
      </div>
    </div>
  );
};
