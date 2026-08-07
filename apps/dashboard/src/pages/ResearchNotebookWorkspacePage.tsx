/**
 * Workspace 10: Research Notebook & Bookmarks Workspace Page
 *
 * Users can create research notes, bookmark edges, bookmark reports, export research,
 * save investigations, and manage versioned notebooks.
 */

import React, { useState } from 'react';

export const ResearchNotebookWorkspacePage: React.FC = () => {
  const [noteTitle, setNoteTitle] = useState('');
  const [noteContent, setNoteContent] = useState('');
  const [notes, setNotes] = useState([
    { id: 'NOT_001', title: 'Boom 1000 Volatility Analysis', content: 'Observed statistical edge persistence during trend expansion regimes.', date: '2026-08-07 12:00 UTC' },
    { id: 'NOT_002', title: 'Walk-Forward Out-of-Sample Results', content: 'Out-of-sample degradation ratio of 0.912 confirms robustness.', date: '2026-08-07 11:30 UTC' },
  ]);

  const handleCreateNote = () => {
    if (!noteTitle || !noteContent) return;
    const newNote = {
      id: `NOT_00${notes.length + 1}`,
      title: noteTitle,
      content: noteContent,
      date: 'Just now',
    };
    setNotes([newNote, ...notes]);
    setNoteTitle('');
    setNoteContent('');
  };

  return (
    <div className="p-6 space-y-6 bg-slate-950 min-h-full text-slate-100">
      <div className="flex justify-between items-center pb-3 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-100 flex items-center gap-2">
            <span className="text-cyan-400">📓</span> Workspace 10: Quantitative Research Notebook & Bookmarks
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Personal quantitative notebook, bookmarks manager, investigation log, and research export suite.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Create Research Note Editor */}
        <div className="bg-slate-900 border border-slate-800 p-5 rounded-lg space-y-4">
          <h3 className="text-sm font-bold text-slate-200">Create New Quantitative Note</h3>
          <input
            type="text"
            placeholder="Note Title (e.g. Boom 1000 Spike Behavior)..."
            value={noteTitle}
            onChange={(e) => setNoteTitle(e.target.value)}
            className="w-full bg-slate-950 border border-slate-700 rounded px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-cyan-500 font-mono"
          />
          <textarea
            placeholder="Markdown Research Content..."
            rows={5}
            value={noteContent}
            onChange={(e) => setNoteContent(e.target.value)}
            className="w-full bg-slate-950 border border-slate-700 rounded px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-cyan-500 font-mono"
          />
          <button
            onClick={handleCreateNote}
            className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded text-xs font-mono font-bold transition-colors"
          >
            + Save Research Note
          </button>
        </div>

        {/* Saved Research Notes List */}
        <div className="bg-slate-900 border border-slate-800 p-5 rounded-lg space-y-3 font-mono text-xs">
          <h3 className="text-sm font-bold text-slate-200 font-sans">Saved Notes ({notes.length})</h3>
          <div className="space-y-3">
            {notes.map((n) => (
              <div key={n.id} className="p-3 bg-slate-950 rounded border border-slate-800 space-y-1">
                <div className="flex justify-between font-bold text-cyan-300">
                  <span>{n.title}</span>
                  <span className="text-[10px] text-slate-500">{n.date}</span>
                </div>
                <div className="text-slate-300 text-[11px]">{n.content}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
