/**
 * Project GOAT v1.0 — Governance Decisions Workspace
 */

import React from 'react';
import { usePipelineStore } from '../stores/pipelineStore';

export const GovernancePage: React.FC = () => {
  const { inspectEntityById } = usePipelineStore();

  const certificates = [
    { id: 'GOV_BOOM500_002', name: 'Institutional Edge Promotion Certificate', approver: 'CQO', quorum: '5/5 Votes', status: 'APPROVED' },
    { id: 'GOV_VOL10_001', name: 'Risk Limit Audit & Compliance Review', approver: 'RISK_MANAGER', quorum: '4/5 Votes', status: 'IN_REVIEW' },
  ];

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
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {certificates.map((item) => (
          <div
            key={item.id}
            onClick={() => inspectEntityById(item.id)}
            className="p-4 bg-slate-900 border border-slate-800 hover:border-cyan-500 rounded-lg cursor-pointer transition-all space-y-3 font-mono"
          >
            <div className="flex justify-between items-center text-xs">
              <span className="font-bold text-cyan-300">{item.id}</span>
              <span className="px-2 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-800 text-[10px]">
                {item.status}
              </span>
            </div>
            <div className="text-sm font-sans font-semibold text-slate-100">{item.name}</div>
            <div className="flex justify-between text-xs text-slate-400 pt-2 border-t border-slate-800">
              <span>Approver: {item.approver}</span>
              <span>Quorum: {item.quorum}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
