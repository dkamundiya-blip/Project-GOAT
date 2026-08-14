/**
 * Project GOAT v1.0 — Governance Decisions Workspace
 */

import React from 'react';
import { usePipelineStore } from '../stores/pipelineStore';

import { useDashboardStore } from '../stores/dashboardStore';

export const GovernancePage: React.FC = () => {
  const { inspectEntityById } = usePipelineStore();
  const governanceDecisions = useDashboardStore((state) => state.governanceDecisions);

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center space-x-2">
            <span>⚖️</span>
            <span>SCIENTIFIC GOVERNANCE WORKSPACE</span>
          </h1>
          <p className="text-xs text-slate-400">
            Quorum decision certificates, promotion approvals, risk limit audits, and institutional signatures.
          </p>
        </div>
        <span className="text-xs font-mono text-cyan-400 bg-slate-900 border border-cyan-900 px-3 py-1 rounded">
          Decisions: {governanceDecisions.length}
        </span>
      </div>

      {governanceDecisions.length === 0 ? (
        <div className="p-8 bg-slate-900/60 border border-dashed border-slate-800 rounded-xl text-center space-y-3">
          <div className="text-2xl">⚖️</div>
          <div className="text-sm font-semibold text-slate-200">NO FORMAL GOVERNANCE DECISIONS RECORDED</div>
          <p className="text-xs text-slate-400 max-w-lg mx-auto">
            The Scientific Governance Engine evaluates candidate edges against constitutional qualification criteria.
            Decisions are recorded when candidates are promoted to live validation or retired.
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-md mx-auto pt-4 text-left font-mono text-xs">
            <div className="p-3 bg-slate-950 rounded border border-slate-800">
              <span className="text-slate-500 block text-[10px]">CONSTITUTIONAL STATUS</span>
              <span className="font-bold text-emerald-300">AMENDMENTS_ENFORCED</span>
            </div>
            <div className="p-3 bg-slate-950 rounded border border-slate-800">
              <span className="text-slate-500 block text-[10px]">SAFETY PROTOCOL</span>
              <span className="font-bold text-cyan-300">RESEARCH_ONLY</span>
            </div>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {governanceDecisions.map((item) => (
            <div
              key={item.decision_id}
              onClick={() => inspectEntityById(item.decision_id)}
              className="p-4 bg-slate-900 border border-slate-800 hover:border-cyan-500 rounded-lg cursor-pointer transition-all space-y-3 font-mono"
            >
              <div className="flex justify-between items-center text-xs">
                <span className="font-bold text-cyan-300">{item.decision_id}</span>
                <span className="px-2 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-800 text-[10px]">
                  {item.outcome}
                </span>
              </div>
              <div className="text-sm font-sans font-semibold text-slate-100">{item.reason}</div>
              <div className="flex justify-between text-xs text-slate-400 pt-2 border-t border-slate-800">
                <span>Edge: {item.edge_id}</span>
                <span>Decided: {item.decided_at}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
