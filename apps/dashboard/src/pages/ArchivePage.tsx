/**
 * Project GOAT v1.0 — Archive Explorer Workspace
 */

import React from 'react';

export const ArchivePage: React.FC = () => {
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
        <span className="text-xs font-mono text-cyan-400 bg-slate-900 border border-cyan-900 px-3 py-1 rounded">
          Archived Records: 0
        </span>
      </div>

      <div className="p-8 bg-slate-900/60 border border-dashed border-slate-800 rounded-xl text-center space-y-3">
        <div className="text-2xl">📦</div>
        <div className="text-sm font-semibold text-slate-200">IMMUTABLE COLD-STORAGE ARCHIVE ONLINE</div>
        <p className="text-xs text-slate-400 max-w-lg mx-auto">
          No retired hypotheses, decayed alpha models, or historical datasets have been archived in this session.
          The institutional archive enforces SHA-256 canonical hashing and deterministic replayability for all retired records.
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-md mx-auto pt-4 text-left font-mono text-xs">
          <div className="p-3 bg-slate-950 rounded border border-slate-800">
            <span className="text-slate-500 block text-[10px]">STORAGE ADAPTER</span>
            <span className="font-bold text-cyan-300">SQLite / archive_records</span>
          </div>
          <div className="p-3 bg-slate-950 rounded border border-slate-800">
            <span className="text-slate-500 block text-[10px]">INTEGRITY HASHING</span>
            <span className="font-bold text-emerald-300">CANONICAL_SHA256</span>
          </div>
        </div>
      </div>
    </div>
  );
};
