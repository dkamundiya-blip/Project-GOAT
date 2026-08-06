/**
 * Project GOAT v1.0 — Archive Explorer Workspace
 */

import React from 'react';
import { usePipelineStore } from '../stores/pipelineStore';

export const ArchivePage: React.FC = () => {
  const { inspectEntityById } = usePipelineStore();

  const archives = [
    { id: 'ARC_CRASH1000_003', name: 'Crash 1000 Regime Switching Cold Archive', records: 450, sha256: 'e3b0c44298fc1c149afbf4c8996fb924', status: 'READ_ONLY' },
    { id: 'ARC_STEPINDEX_004', name: 'Step Index Decayed Hypothesis Archive', records: 120, sha256: 'f4c8996fb92427ae41e4649b934ca495', status: 'READ_ONLY' },
  ];

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center space-x-2">
            <span>📦</span>
            <span>INSTITUTIONAL ARCHIVE EXPLORER</span>
          </h1>
          <p className="text-xs text-slate-400">
            Immutable cold-storage archive browsing, historical audit records, and retired hypothesis lineage.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {archives.map((item) => (
          <div
            key={item.id}
            onClick={() => inspectEntityById(item.id)}
            className="p-4 bg-slate-900 border border-slate-800 hover:border-cyan-500 rounded-lg cursor-pointer transition-all space-y-3 font-mono"
          >
            <div className="flex justify-between items-center text-xs">
              <span className="font-bold text-cyan-300">{item.id}</span>
              <span className="px-2 py-0.5 rounded bg-slate-950 text-slate-400 border border-slate-800 text-[10px]">
                {item.status}
              </span>
            </div>
            <div className="text-sm font-sans font-semibold text-slate-100">{item.name}</div>
            <div className="flex justify-between text-xs text-slate-400 pt-2 border-t border-slate-800">
              <span>Records: {item.records}</span>
              <span>SHA-256: {item.sha256.substring(0, 8)}...</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
