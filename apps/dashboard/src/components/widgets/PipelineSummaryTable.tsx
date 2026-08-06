/**
 * Project GOAT v1.0 — Active Research Pipeline Summary Table Widget
 */

import React from 'react';

export const PipelineSummaryTable: React.FC = () => {
  const items = [
    { id: 'HYP_VOL_REGIME_01', title: 'Volatility Cluster Regime Inversion', category: 'MICROSTRUCTURE', status: 'VERIFIED', score: '0.88' },
    { id: 'HYP_JUMP_REVERSI_02', title: 'Synthetic Jump Reversal Expectancy', category: 'STATISTICAL_EDGE', status: 'PROMOTED', score: '0.93' },
    { id: 'HYP_MOM_BREAK_03', title: 'Momentum Breakout False Discovery', category: 'ALPHA_CANDIDATE', status: 'IN_EXPERIMENT', score: '0.76' },
    { id: 'HYP_REGIME_SHIFT_04', title: 'Markov Regime Transition Memory', category: 'MARKET_STATE', status: 'EVIDENCE_COLLECTED', score: '0.82' },
  ];

  return (
    <div className="bg-slate-900 border border-slate-800 rounded p-4 shadow-md">
      <h3 className="text-sm font-semibold uppercase tracking-wider text-amber-400 mb-4">
        Active Quantitative Research Pipeline
      </h3>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] tracking-wider">
            <tr>
              <th className="py-2 px-3">Hypothesis ID</th>
              <th className="py-2 px-3">Title / Subject</th>
              <th className="py-2 px-3">Category</th>
              <th className="py-2 px-3">Pipeline Status</th>
              <th className="py-2 px-3">Confidence Score</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {items.map((item) => (
              <tr key={item.id} className="hover:bg-slate-850">
                <td className="py-2 px-3 font-mono text-cyan-400">{item.id}</td>
                <td className="py-2 px-3 font-semibold text-slate-200">{item.title}</td>
                <td className="py-2 px-3"><span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300">{item.category}</span></td>
                <td className="py-2 px-3"><span className="text-emerald-400 font-bold">{item.status}</span></td>
                <td className="py-2 px-3 font-mono text-amber-400">{item.score}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
