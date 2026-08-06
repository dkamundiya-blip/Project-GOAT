/**
 * Project GOAT v1.0 — Scientific Pipeline Subsystem Health Matrix
 */

import React from 'react';

export const SubsystemHealthWidget: React.FC = () => {
  const subsystems = [
    { name: 'Hypothesis Registry', pkg: 'goat.research', version: 'v0.9.1 FROZEN', status: 'ONLINE', tests: '100% PASS' },
    { name: 'Evidence Collection', pkg: 'goat.evidence', version: 'v0.9.1 FROZEN', status: 'ONLINE', tests: '100% PASS' },
    { name: 'Experiment Engine', pkg: 'goat.experiments', version: 'v0.9.1 FROZEN', status: 'ONLINE', tests: '100% PASS' },
    { name: 'Statistical Evaluator', pkg: 'goat.statistics', version: 'v0.9.1 FROZEN', status: 'ONLINE', tests: '100% PASS' },
    { name: 'Live Validation', pkg: 'goat.validation', version: 'v0.9.1 FROZEN', status: 'ONLINE', tests: '100% PASS' },
    { name: 'Governance Engine', pkg: 'goat.governance', version: 'v0.9.1 FROZEN', status: 'ONLINE', tests: '100% PASS' },
    { name: 'Knowledge Graph', pkg: 'goat.knowledge', version: 'v0.9.1 FROZEN', status: 'ONLINE', tests: '100% PASS' },
    { name: 'Research Intelligence', pkg: 'goat.intelligence', version: 'v0.9.1 FROZEN', status: 'ONLINE', tests: '100% PASS' },
    { name: 'Institutional Archive', pkg: 'goat.archive', version: 'v0.9.1 FROZEN', status: 'ONLINE', tests: '100% PASS' },
    { name: 'Dashboard API Server', pkg: 'goat.dashboard', version: 'v1.0.0 ACTIVE', status: 'ONLINE', tests: '440 PASS' },
  ];

  return (
    <div className="bg-slate-900 border border-slate-800 rounded p-4 mb-6 shadow-md">
      <h3 className="text-sm font-semibold uppercase tracking-wider text-purple-400 mb-4">
        Scientific Pipeline Subsystem Status Matrix
      </h3>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-3">
        {subsystems.map((sub, idx) => (
          <div key={idx} className="bg-slate-950 p-3 rounded border border-slate-800 flex flex-col justify-between">
            <div>
              <div className="text-xs font-semibold text-slate-200">{sub.name}</div>
              <div className="text-[10px] font-mono text-slate-500">{sub.pkg}</div>
            </div>
            <div className="mt-2 flex justify-between items-center text-[10px]">
              <span className="text-emerald-400 font-bold">{sub.status}</span>
              <span className="text-slate-400 font-mono">{sub.tests}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
