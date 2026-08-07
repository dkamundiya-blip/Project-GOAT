/**
 * Institutional Command Palette Component
 *
 * Supports global keyboard shortcut (Ctrl+K / Cmd+K) for instant workspace navigation,
 * symbol switching, edge lookup, hypothesis search, and command execution.
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export const CommandPalette: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        setIsOpen((prev) => !prev);
      } else if (e.key === 'Escape') {
        setIsOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const commands = [
    { title: 'Workspace 1: Research Center', path: '/research-center', category: 'WORKSPACES' },
    { title: 'Workspace 2: Market Intelligence Dashboard', path: '/market-intelligence-ws', category: 'WORKSPACES' },
    { title: 'Workspace 3: Edge Laboratory', path: '/edge-laboratory', category: 'WORKSPACES' },
    { title: 'Workspace 4: Evidence Explorer', path: '/evidence-explorer', category: 'WORKSPACES' },
    { title: 'Workspace 5: AI Research Assistant', path: '/ai-research-assistant', category: 'WORKSPACES' },
    { title: 'Workspace 6: Research Timeline', path: '/research-timeline', category: 'WORKSPACES' },
    { title: 'Workspace 7: Knowledge Graph Explorer', path: '/knowledge-graph', category: 'WORKSPACES' },
    { title: 'Workspace 8: System Health Center', path: '/system-health', category: 'WORKSPACES' },
    { title: 'Workspace 9: Portfolio Research', path: '/portfolio-research', category: 'WORKSPACES' },
    { title: 'Workspace 10: Research Notebook & Bookmarks', path: '/research-notebook', category: 'WORKSPACES' },
    { title: 'System Validation Dashboard', path: '/system-validation', category: 'SYSTEM' },
    { title: 'Inspect Top Edge (EDG_00018F42A109C3E1)', path: '/edge-laboratory', category: 'EDGES' },
  ];

  const filteredCommands = commands.filter(
    (c) => c.title.toLowerCase().includes(query.toLowerCase()) || c.category.toLowerCase().includes(query.toLowerCase())
  );

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-start justify-center pt-20">
      <div className="bg-slate-900 border border-slate-700 w-full max-w-xl rounded-xl shadow-2xl overflow-hidden font-mono text-xs">
        <div className="p-3 border-b border-slate-800 flex items-center gap-2">
          <span className="text-slate-400">🔍</span>
          <input
            type="text"
            autoFocus
            placeholder="Type a command or search workspace (e.g. Edge, Notebook, Ctrl+K)..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full bg-transparent text-slate-100 placeholder-slate-500 focus:outline-none"
          />
          <kbd className="px-2 py-0.5 bg-slate-800 text-[10px] text-slate-400 rounded">ESC</kbd>
        </div>

        <div className="max-h-80 overflow-y-auto p-2 space-y-1">
          {filteredCommands.length > 0 ? (
            filteredCommands.map((cmd, idx) => (
              <div
                key={idx}
                onClick={() => {
                  navigate(cmd.path);
                  setIsOpen(false);
                }}
                className="p-2.5 rounded hover:bg-slate-800 cursor-pointer flex justify-between items-center text-slate-200 transition-colors"
              >
                <span className="font-semibold">{cmd.title}</span>
                <span className="text-[10px] px-2 py-0.5 rounded bg-slate-950 text-slate-400 border border-slate-800">
                  {cmd.category}
                </span>
              </div>
            ))
          ) : (
            <div className="p-4 text-center text-slate-500">No matching commands found.</div>
          )}
        </div>
      </div>
    </div>
  );
};
