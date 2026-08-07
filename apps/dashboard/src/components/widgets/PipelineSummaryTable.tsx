/**
 * Project GOAT v1.0 — Active Research Pipeline Summary Table Widget
 *
 * 100% bound to real-time live telemetry store & discovered edges.
 * ZERO hardcoded rows.
 */

import React from 'react';
import { useTelemetryStore } from '../../stores/telemetryStore';

export const PipelineSummaryTable: React.FC = () => {
  const edges = useTelemetryStore((s) => s.edges);
  const symbol = useTelemetryStore((s) => s.symbol);

  return (
    <div className="bg-slate-900 border border-slate-800 rounded p-4 shadow-md font-sans">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-amber-400">
          Active Quantitative Research Pipeline ({symbol})
        </h3>
        <span className="text-xs font-mono text-slate-400">
          {edges.length} Discovered Edges Evaluated
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] tracking-wider">
            <tr>
              <th className="py-2 px-3">Edge / Hypothesis ID</th>
              <th className="py-2 px-3">Instrument</th>
              <th className="py-2 px-3">Attributed Features</th>
              <th className="py-2 px-3">Pipeline Status</th>
              <th className="py-2 px-3">Expected Value</th>
              <th className="py-2 px-3">Confidence Score</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800 font-mono text-xs">
            {edges.length === 0 ? (
              <tr>
                <td colSpan={6} className="py-6 text-center text-slate-500 font-mono text-xs">
                  Streaming telemetry connected. Awaiting discovered edge hypotheses from backend...
                </td>
              </tr>
            ) : (
              edges.map((item) => (
                <tr key={item.id} className="hover:bg-slate-850">
                  <td className="py-2 px-3 text-cyan-400 font-bold">{item.id}</td>
                  <td className="py-2 px-3 font-semibold text-slate-200">{item.symbol}</td>
                  <td className="py-2 px-3">
                    <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 text-[10px]">
                      {item.features}
                    </span>
                  </td>
                  <td className="py-2 px-3">
                    <span className="text-emerald-400 font-bold text-[10px] px-2 py-0.5 rounded bg-emerald-950/80 border border-emerald-800">
                      {item.status}
                    </span>
                  </td>
                  <td className="py-2 px-3 text-emerald-300 font-bold">+{(item.ev * 100).toFixed(2)}%</td>
                  <td className="py-2 px-3 text-amber-400 font-bold">{item.score}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
