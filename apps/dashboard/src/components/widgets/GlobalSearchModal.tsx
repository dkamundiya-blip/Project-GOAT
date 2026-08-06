/**
 * Project GOAT v1.0 — Global Canonical Search Modal Widget
 * Step 1.4 Presentation Layer Upgrade
 */

import React, { useEffect, useState } from 'react';
import { useSearchStore } from '../../stores/searchStore';
import { usePipelineStore } from '../../stores/pipelineStore';

export const GlobalSearchModal: React.FC = () => {
  const { searchOpen, query, results, history, setSearchOpen, setQuery, clearSearch } = useSearchStore();
  const { inspectEntityById } = usePipelineStore();
  const [selectedIndex, setSelectedIndex] = useState<number>(0);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setSearchOpen(!searchOpen);
      }
      if (!searchOpen) return;

      if (e.key === 'Escape') {
        setSearchOpen(false);
      } else if (e.key === 'ArrowDown') {
        e.preventDefault();
        setSelectedIndex((prev) => (results.length > 0 ? (prev + 1) % results.length : 0));
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setSelectedIndex((prev) => (results.length > 0 ? (prev - 1 + results.length) % results.length : 0));
      } else if (e.key === 'Enter' && results.length > 0) {
        e.preventDefault();
        const selected = results[selectedIndex] || results[0];
        if (selected) {
          inspectEntityById(selected.canonicalId);
          setSearchOpen(false);
        }
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [searchOpen, setSearchOpen, results, selectedIndex, inspectEntityById]);

  if (!searchOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-20 bg-slate-950/80 backdrop-blur-md p-4 font-mono">
      <div className="bg-[#0b101b] border border-slate-700/80 rounded-xl w-full max-w-2xl shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-150">
        {/* Search Header Input */}
        <div className="flex items-center border-b border-slate-800 px-4 py-3.5 bg-[#06090e]">
          <span className="text-cyan-400 text-lg mr-3">🔍</span>
          <input
            type="text"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setSelectedIndex(0);
            }}
            placeholder="Search Canonical ID (HYP_, EVI_, EXP_, STA_, VAL_, GOV_, KNO_, ARC_, INT_)..."
            className="w-full bg-transparent text-sm text-slate-100 placeholder-slate-500 focus:outline-none"
            autoFocus
          />
          {query && (
            <button onClick={clearSearch} className="text-xs text-slate-400 hover:text-slate-200 px-2 py-1">
              Clear
            </button>
          )}
          <button
            onClick={() => setSearchOpen(false)}
            className="ml-2 text-xs font-mono bg-slate-800 hover:bg-slate-700 text-slate-300 px-2 py-1 rounded"
          >
            ESC
          </button>
        </div>

        {/* Results Body */}
        <div className="max-h-96 overflow-y-auto p-4 space-y-2">
          {query && results.length === 0 && (
            <div className="py-8 text-center text-slate-400 text-xs">
              No matching canonical entities found for "<span className="text-cyan-400 font-bold">{query}</span>"
            </div>
          )}

          {!query && (
            <div>
              <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-2">RECENT CANONICAL SEARCHES</div>
              <div className="flex flex-wrap gap-2">
                {history.map((h) => (
                  <button
                    key={h}
                    onClick={() => setQuery(h)}
                    className="text-xs bg-[#06090e] border border-slate-800 hover:border-cyan-500 text-cyan-400 px-2.5 py-1 rounded-md"
                  >
                    {h}
                  </button>
                ))}
              </div>
            </div>
          )}

          {results.map((item, idx) => {
            const isFocused = idx === selectedIndex;
            return (
              <div
                key={item.id}
                onClick={() => {
                  inspectEntityById(item.canonicalId);
                  setSearchOpen(false);
                }}
                className={`p-3 rounded-lg border cursor-pointer transition-all ${
                  isFocused
                    ? 'bg-slate-800 border-cyan-500 shadow-md ring-1 ring-cyan-500/40'
                    : 'bg-[#06090e]/70 border-slate-800 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-bold text-cyan-300">{item.canonicalId}</span>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-purple-950/80 text-purple-300 border border-purple-800/80">
                    {item.stage}
                  </span>
                </div>
                <div className="text-xs font-semibold text-slate-200 mb-1 font-sans">{item.title}</div>
                <div className="text-[11px] text-slate-400">{item.snippet}</div>
              </div>
            );
          })}
        </div>

        {/* Modal Footer */}
        <div className="border-t border-slate-800 px-4 py-2 bg-[#06090e] text-[10.5px] text-slate-500 flex justify-between">
          <span>Use ▲ ▼ to navigate, Enter to inspect</span>
          <span>Shortcut: Ctrl + K</span>
        </div>
      </div>
    </div>
  );
};
