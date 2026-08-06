/**
 * Project GOAT v1.0 — Evidence Collections Workspace
 */

import React from 'react';
import { usePipelineStore } from '../stores/pipelineStore';

export const EvidencePage: React.FC = () => {
  const { inspectEntityById } = usePipelineStore();

  const evidenceRecords = [
    { id: 'EVI_VOL10_001', title: 'Volatility 10 High-Frequency Tick Evidence', samples: 10000000, stationarity: '0.999', status: 'VERIFIED' },
    { id: 'EVI_BOOM500_002', title: 'Boom 500 Spike Reversion Dataset', samples: 8500000, stationarity: '0.995', status: 'VERIFIED' },
  ];

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center space-x-2">
            <span>📑</span>
            <span>EVIDENCE COLLECTIONS WORKSPACE</span>
          </h1>
          <p className="text-xs text-slate-400">
            Empirical tick datasets, stationarity metrics, and statistical sample records.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {evidenceRecords.map((item) => (
          <div
            key={item.id}
            onClick={() => inspectEntityById(item.id)}
            className="p-4 bg-slate-900 border border-slate-800 hover:border-cyan-500 rounded-lg cursor-pointer transition-all space-y-3 font-mono"
          >
            <div className="flex justify-between items-center text-xs">
              <span className="font-bold text-cyan-300">{item.id}</span>
              <span className="px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800 text-[10px]">
                {item.status}
              </span>
            </div>
            <div className="text-sm font-sans font-semibold text-slate-100">{item.title}</div>
            <div className="flex justify-between text-xs text-slate-400 pt-2 border-t border-slate-800">
              <span>Samples: {item.samples.toLocaleString()}</span>
              <span>ADF Score: {item.stationarity}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
