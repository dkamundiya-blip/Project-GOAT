import React from 'react';

export const ShimmerCard: React.FC = () => (
  <div className="bg-[#0b101b]/80 border border-slate-800/80 p-4 rounded-xl shadow-lg animate-pulse space-y-3">
    <div className="flex justify-between items-center">
      <div className="h-4 w-28 bg-slate-800 rounded" />
      <div className="h-5 w-5 bg-slate-800 rounded-full" />
    </div>
    <div className="h-7 w-32 bg-slate-800 rounded" />
    <div className="h-3 w-20 bg-slate-800 rounded" />
  </div>
);

export const ShimmerTable: React.FC = () => (
  <div className="bg-[#0b101b]/90 border border-slate-800/80 rounded-xl p-4 shadow-xl animate-pulse space-y-3">
    <div className="h-6 w-48 bg-slate-800 rounded mb-4" />
    {Array.from({ length: 5 }).map((_, i) => (
      <div key={i} className="h-10 w-full bg-slate-900/80 rounded" />
    ))}
  </div>
);

export const OfflineBanner: React.FC<{ onRetry?: () => void }> = ({ onRetry }) => (
  <div className="bg-amber-950/40 border border-amber-800/60 p-4 rounded-xl text-amber-200 flex items-center justify-between font-mono text-xs mb-4">
    <div className="flex items-center gap-2">
      <span>⚠️</span>
      <span>BACKEND CONNECTION TEMPORARILY OFFLINE — RECONNECTING AUTOMATICALLY...</span>
    </div>
    {onRetry && (
      <button
        onClick={onRetry}
        className="px-3 py-1 bg-amber-900/80 hover:bg-amber-800 text-amber-100 font-bold rounded border border-amber-700"
      >
        Retry Now
      </button>
    )}
  </div>
);

export const EmptyState: React.FC<{ title: string; message: string; actionText?: string; onAction?: () => void }> = ({
  title,
  message,
  actionText,
  onAction,
}) => (
  <div className="p-12 text-center bg-[#0b101b]/60 border border-slate-800/80 rounded-xl font-mono space-y-3">
    <div className="text-3xl">🔍</div>
    <div className="text-sm font-bold text-slate-200">{title}</div>
    <div className="text-xs text-slate-400 max-w-md mx-auto">{message}</div>
    {actionText && onAction && (
      <button
        onClick={onAction}
        className="mt-2 px-4 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-bold text-xs rounded-md transition-colors"
      >
        {actionText}
      </button>
    )}
  </div>
);
