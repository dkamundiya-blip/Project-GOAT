import React, { useState } from 'react';
import { useNotificationStore } from '../../stores/notificationStore';

interface NotificationCenterProps {
  isOpen: boolean;
  onClose: () => void;
}

export const NotificationCenter: React.FC<NotificationCenterProps> = ({ isOpen, onClose }) => {
  const { notifications, clearNotifications, markAsRead } = useNotificationStore();
  const [filterSeverity, setFilterSeverity] = useState<'ALL' | 'INFO' | 'WARN' | 'CRITICAL'>('ALL');

  if (!isOpen) return null;

  const getSev = (n: any) => (n.severity || n.type || 'INFO').toUpperCase();

  const filtered = notifications.filter(
    (n) => filterSeverity === 'ALL' || getSev(n) === filterSeverity
  );

  return (
    <div className="fixed inset-y-0 right-0 z-50 w-96 bg-[#0b101b]/95 backdrop-blur-xl border-l border-slate-800 shadow-2xl flex flex-col transition-all duration-300">
      {/* Header */}
      <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-[#06090e]/80">
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-cyan-400 animate-pulse" />
          <h3 className="text-sm font-semibold text-slate-100 font-mono tracking-wider">SYSTEM NOTIFICATION CENTER</h3>
        </div>
        <button
          onClick={onClose}
          className="text-slate-400 hover:text-slate-100 text-lg font-mono px-2 py-1 rounded hover:bg-slate-800 transition-colors"
          aria-label="Close Notification Center"
        >
          ✕
        </button>
      </div>

      {/* Filter Tabs */}
      <div className="flex border-b border-slate-800/80 bg-[#0b101b] text-xs font-mono">
        {(['ALL', 'INFO', 'WARN', 'CRITICAL'] as const).map((sev) => (
          <button
            key={sev}
            onClick={() => setFilterSeverity(sev)}
            className={`flex-1 py-2 text-center transition-colors border-b-2 ${
              filterSeverity === sev
                ? 'border-cyan-500 text-cyan-400 font-semibold bg-slate-900/50'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            {sev}
          </button>
        ))}
      </div>

      {/* List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {filtered.length === 0 ? (
          <div className="text-center py-12 text-slate-500 font-mono text-xs">
            NO SYSTEM ALERTS MATCHING CRITERIA
          </div>
        ) : (
          filtered.map((n) => {
            const sev = getSev(n);
            return (
              <div
                key={n.id}
                onClick={() => markAsRead(n.id)}
                className={`p-3 rounded-lg border text-xs transition-all cursor-pointer ${
                  sev === 'CRITICAL' || sev === 'ERROR'
                    ? 'bg-rose-950/20 border-rose-800/50 text-rose-200 hover:border-rose-600'
                    : sev === 'WARN' || sev === 'WARNING'
                    ? 'bg-amber-950/20 border-amber-800/50 text-amber-200 hover:border-amber-600'
                    : 'bg-slate-900/60 border-slate-800 text-slate-300 hover:border-slate-700'
                } ${!n.read ? 'ring-1 ring-cyan-500/50' : 'opacity-80'}`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="font-mono text-[10px] font-bold px-1.5 py-0.5 rounded bg-slate-800/80 uppercase">
                    {sev}
                  </span>
                  <span className="font-mono text-[10px] text-slate-500">{n.timestamp}</span>
                </div>
                <p className="font-sans font-medium mb-1">{n.title || n.message}</p>
                {n.detail && <p className="font-mono text-[11px] text-slate-400">{n.detail}</p>}
              </div>
            );
          })
        )}
      </div>

      {/* Footer */}
      <div className="p-3 border-t border-slate-800 bg-[#06090e]/80 flex justify-between items-center text-xs font-mono">
        <span className="text-slate-500">{notifications.length} Total Logged</span>
        <button
          onClick={clearNotifications}
          className="text-rose-400 hover:text-rose-300 hover:underline text-[11px]"
        >
          Clear History
        </button>
      </div>
    </div>
  );
};
