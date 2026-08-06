/**
 * Project GOAT v1.0 — Research Intelligence Workspace
 */

import React from 'react';
import { usePipelineStore } from '../stores/pipelineStore';

export const ResearchIntelligencePage: React.FC = () => {
  const { inspectEntityById } = usePipelineStore();

  const intelligenceReports = [
    { id: 'INT_VOL10_001', name: 'Cross-Market Microstructure Correlation Matrix', alphaDecay: '9.4 Months', confidence: '98.5%', status: 'HIGH_CONVICTION' },
    { id: 'INT_BOOM500_002', name: 'Vol-of-Vol Perturbation Resilience Report', alphaDecay: '14.2 Months', confidence: '99.1%', status: 'HIGH_CONVICTION' },
  ];

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center space-x-2">
            <span>💡</span>
            <span>RESEARCH INTELLIGENCE WORKSPACE</span>
          </h1>
          <p className="text-xs text-slate-400">
            Institutional research insights, cross-dataset correlation matrices, and alpha decay forecasts.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {intelligenceReports.map((item) => (
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
            <div className="text-sm font-sans font-semibold text-slate-100">{item.name}</div>
            <div className="flex justify-between text-xs text-slate-400 pt-2 border-t border-slate-800">
              <span>Forecast Decay: {item.alphaDecay}</span>
              <span>Confidence: {item.confidence}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
