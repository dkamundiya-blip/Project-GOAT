/**
 * Project GOAT v1.0 — Live Validation Workspace
 */

import React from 'react';
import { usePipelineStore } from '../stores/pipelineStore';

export const LiveValidationPage: React.FC = () => {
  const { inspectEntityById } = usePipelineStore();

  const sessions = [
    { id: 'VAL_VOL10_001', name: 'Paper Trading Validation Session #101', trades: 1420, fillSlippage: '0.00ms', status: 'LIVE_STREAMING' },
    { id: 'VAL_BOOM500_002', name: 'Paper Trading Validation Session #102', trades: 2150, fillSlippage: '0.00ms', status: 'PASSED' },
  ];

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
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {sessions.map((item) => (
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
              <span>Trades: {item.trades.toLocaleString()}</span>
              <span>Slippage: {item.fillSlippage}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
