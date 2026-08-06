/**
 * Project GOAT v1.0 — Institutional Top Navigation Bar
 * Step 1.4 Presentation Layer Upgrade
 */

import React from 'react';
import { useHealthStore } from '../../stores/healthStore';
import { useConnectionStore } from '../../stores/connectionStore';
import { useSessionStore } from '../../stores/sessionStore';
import { useNotificationStore } from '../../stores/notificationStore';
import { useSearchStore } from '../../stores/searchStore';
import { useTheme } from '../../theme/useTheme';

interface TopNavProps {
  onToggleNotificationCenter?: () => void;
}

export const TopNav: React.FC<TopNavProps> = ({ onToggleNotificationCenter }) => {
  const { healthStatus } = useHealthStore();
  const { wsState, restConnected } = useConnectionStore();
  const { activeSession } = useSessionStore();
  const { unreadCount } = useNotificationStore();
  const { setSearchOpen } = useSearchStore();
  const { mode, toggleTheme } = useTheme();

  return (
    <header className="h-14 bg-[#06090e]/90 backdrop-blur-xl border-b border-slate-800/80 px-4 flex items-center justify-between select-none z-30 sticky top-0">
      {/* Brand & System Status */}
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-cyan-500 via-blue-600 to-indigo-600 flex items-center justify-center font-bold text-xs text-slate-950 shadow-lg shadow-cyan-500/20 ring-1 ring-white/20">
            GT
          </div>
          <div>
            <span className="font-bold text-sm tracking-wider text-slate-100 font-mono flex items-center gap-1.5">
              PROJECT GOAT <span className="text-[10px] px-1.5 py-0.2 rounded bg-cyan-950/80 border border-cyan-800/60 text-cyan-400 font-mono">v1.0</span>
            </span>
            <span className="text-[10px] text-slate-500 font-mono block -mt-0.5">INSTITUTIONAL QUANT TERMINAL</span>
          </div>
        </div>

        <div className="h-5 w-px bg-slate-800/80" />

        {/* Global Search Quick Trigger */}
        <button
          onClick={() => setSearchOpen(true)}
          className="flex items-center space-x-2 bg-slate-900/80 border border-slate-800 hover:border-cyan-500/50 px-3 py-1.5 rounded-md text-xs text-slate-400 font-mono transition-all hover:bg-slate-800/80 shadow-sm"
        >
          <span>🔍</span>
          <span className="hidden sm:inline">Search Canonical IDs...</span>
          <span className="bg-slate-950 border border-slate-800 px-1.5 py-0.5 rounded text-[10px] text-slate-500 font-semibold">
            Ctrl+K
          </span>
        </button>

        {/* Server Status Badge */}
        <div className="hidden md:flex items-center space-x-2 bg-emerald-950/30 border border-emerald-800/40 px-2.5 py-1 rounded-md">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <span className="text-xs font-mono font-semibold text-emerald-400">
            {healthStatus?.serverStatus || 'ONLINE'}
          </span>
        </div>
      </div>

      {/* Connection & User Controls */}
      <div className="flex items-center space-x-3 font-mono text-xs">
        <div className="hidden lg:flex items-center space-x-3 bg-slate-900/80 px-3 py-1 rounded-md border border-slate-800">
          <div className="flex items-center space-x-1.5">
            <span className="text-[10px] text-slate-500">REST:</span>
            <span className={restConnected ? 'text-emerald-400 font-semibold' : 'text-rose-400 font-semibold'}>
              {restConnected ? 'CONNECTED' : 'OFFLINE'}
            </span>
          </div>
          <div className="w-px h-3 bg-slate-800" />
          <div className="flex items-center space-x-1.5">
            <span className="text-[10px] text-slate-500">WS:</span>
            <span className={wsState === 'OPEN' ? 'text-emerald-400 font-semibold' : 'text-amber-400 font-semibold'}>
              {wsState}
            </span>
          </div>
        </div>

        {/* Theme Mode Toggle */}
        <button
          onClick={toggleTheme}
          title={`Switch Theme (Current: ${mode})`}
          className="p-1.5 bg-slate-900/80 hover:bg-slate-800 border border-slate-800 rounded-md text-slate-300 transition-colors"
        >
          {mode === 'dark' ? '🌙' : '👁️'}
        </button>

        {/* Notifications Icon */}
        <button
          onClick={onToggleNotificationCenter}
          className="relative p-1.5 bg-slate-900/80 hover:bg-slate-800 border border-slate-800 rounded-md text-slate-300 transition-colors"
          aria-label="Toggle Notification Center"
        >
          <span className="text-sm">🔔</span>
          {unreadCount > 0 && (
            <span className="absolute -top-1 -right-1 bg-rose-500 text-slate-950 font-bold text-[9px] w-4 h-4 rounded-full flex items-center justify-center animate-pulse">
              {unreadCount}
            </span>
          )}
        </button>

        {/* User Account Menu */}
        <div className="flex items-center space-x-2 bg-slate-900/80 px-3 py-1 rounded-md border border-slate-800">
          <div className="w-5 h-5 rounded bg-cyan-950 border border-cyan-700/60 text-cyan-400 text-[10px] font-bold flex items-center justify-center">
            {activeSession?.userRole ? activeSession.userRole[0] : 'Q'}
          </div>
          <span className="text-slate-200 text-xs font-semibold">{activeSession?.userRole || 'QUANT_OPERATOR'}</span>
        </div>
      </div>
    </header>
  );
};
