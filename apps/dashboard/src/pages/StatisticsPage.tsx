/**
 * Project GOAT v1.0 — Statistical Evaluation Workspace
 */

import React from 'react';
import { usePipelineStore } from '../stores/pipelineStore';

export const StatisticsPage: React.FC = () => {
  const { inspectEntityById } = usePipelineStore();

  const stats = [
    { id: 'STA_VOL10_001', name: 'Sharpe & p-Value Statistical Evaluation', sharpe: 2.85, pValue: 0.0012, tStat: 4.82, status: 'SIGNIFICANT' },
    { id: 'STA_BOOM500_002', name: 'Non-Parametric Stationarity Evaluation', sharpe: 3.12, pValue: 0.0004, tStat: 5.21, status: 'SIGNIFICANT' },
  ];

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center space-x-2">
            <span>📈</span>
            <span>STATISTICAL EVALUATOR WORKSPACE</span>
          </h1>
          <p className="text-xs text-slate-400">
            Rigorous statistical significance evaluation, Sharpe ratios, p-values, and t-statistics.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {stats.map((item) => (
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
              <span>Sharpe: {item.sharpe}</span>
              <span>p-val: {item.pValue}</span>
              <span>t-stat: {item.tStat}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
