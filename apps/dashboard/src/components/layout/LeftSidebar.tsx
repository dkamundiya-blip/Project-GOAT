/**
 * Project GOAT v1.0 — Institutional Left Navigation Sidebar
 * Step 1.4 Presentation Layer Upgrade
 */

import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';

export const LeftSidebar: React.FC = () => {
  const [isCollapsed, setIsCollapsed] = useState(false);

  const navGroups = [
    {
      group: 'Operator Workstation',
      items: [
        { id: 'dashboard', label: 'Overview Control Room', path: '/', icon: '📊', badge: 'LIVE' },
        { id: 'control-room', label: 'Control Room Workstation', path: '/control-room', icon: '🖥️' },
        { id: 'markets', label: 'Markets Overview', path: '/markets', icon: '💹' },
      ],
    },
    {
      group: 'Scientific Pipeline',
      items: [
        { id: 'research', label: 'Research Hypotheses', path: '/research', icon: '🔬', badge: 'STAGE 1' },
        { id: 'evidence', label: 'Evidence Collection', path: '/evidence', icon: '📑', badge: 'STAGE 2' },
        { id: 'experiments', label: 'Experiment Engine', path: '/experiments', icon: '🧪', badge: 'STAGE 3' },
        { id: 'statistics', label: 'Statistical Evaluator', path: '/statistics', icon: '📈', badge: 'STAGE 4' },
        { id: 'live-validation', label: 'Live Validation', path: '/live-validation', icon: '⚡', badge: 'STAGE 5' },
        { id: 'governance', label: 'Scientific Governance', path: '/governance', icon: '⚖️', badge: 'STAGE 6' },
      ],
    },
    {
      group: 'Knowledge & Intelligence',
      items: [
        { id: 'knowledge-graph', label: 'Knowledge Graph', path: '/knowledge-graph', icon: '🕸️' },
        { id: 'edge-discovery', label: 'Edge Discovery', path: '/edge-discovery', icon: '🔍' },
        { id: 'research-intelligence', label: 'Research Intelligence', path: '/research-intelligence', icon: '💡' },
        { id: 'archive', label: 'Institutional Archive', path: '/archive', icon: '📦', badge: 'STAGE 7' },
        { id: 'portfolio', label: 'Portfolio Preview', path: '/portfolio', icon: '💼' },
      ],
    },
    {
      group: 'System Operations',
      items: [
        { id: 'monitoring', label: 'System Telemetry', path: '/monitoring', icon: '🖥️' },
        { id: 'settings', label: 'Workstation Settings', path: '/settings', icon: '⚙️' },
      ],
    },
  ];

  return (
    <aside
      className={`${
        isCollapsed ? 'w-16' : 'w-64'
      } bg-[#06090e]/95 backdrop-blur-xl border-r border-slate-800/80 flex flex-col justify-between select-none transition-all duration-300 z-20`}
    >
      {/* Sidebar Header & Collapse Toggle */}
      <div className="p-3 border-b border-slate-800/60 flex items-center justify-between">
        {!isCollapsed && (
          <span className="text-[11px] font-mono font-semibold text-slate-400 uppercase tracking-wider">
            WORKSTATION NAV
          </span>
        )}
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition-colors mx-auto"
          title={isCollapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
          aria-label={isCollapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
        >
          {isCollapsed ? '⏩' : '⏪'}
        </button>
      </div>

      {/* Navigation Groups */}
      <div className="flex-1 p-2 overflow-y-auto space-y-4 font-mono">
        {navGroups.map((group, idx) => (
          <div key={idx}>
            {!isCollapsed && (
              <div className="px-2 text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-1.5 flex items-center gap-1">
                <span className="text-cyan-500">▶</span> {group.group}
              </div>
            )}
            <div className="space-y-0.5">
              {group.items.map((item) => (
                <NavLink
                  key={item.path}
                  to={item.path}
                  data-item-id={item.id}
                  title={isCollapsed ? item.label : undefined}
                  className={({ isActive }) =>
                    `flex items-center ${
                      isCollapsed ? 'justify-center py-2.5 px-0' : 'justify-between px-2.5 py-1.5'
                    } rounded-md text-xs transition-all ${
                      isActive
                        ? 'bg-cyan-950/80 text-cyan-300 font-semibold border-l-2 border-cyan-400 shadow-sm shadow-cyan-950/50'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
                    }`
                  }
                >
                  <div className="flex items-center space-x-2.5">
                    <span className="text-sm">{item.icon}</span>
                    {!isCollapsed && <span>{item.label}</span>}
                  </div>
                  {!isCollapsed && item.badge && (
                    <span className="text-[9px] font-mono px-1.5 py-0.2 rounded bg-slate-800/80 border border-slate-700/60 text-slate-400">
                      {item.badge}
                    </span>
                  )}
                </NavLink>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Footer */}
      {!isCollapsed && (
        <div className="p-3 border-t border-slate-900/80 text-[10px] text-slate-500 font-mono flex items-center justify-between">
          <span className="flex items-center gap-1">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" /> INSTITUTIONAL TERMINAL
          </span>
          <span className="text-slate-600">v1.0.0</span>
        </div>
      )}
    </aside>
  );
};
