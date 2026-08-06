import React from 'react';
import { Breadcrumbs } from './Breadcrumbs';

interface WorkspaceHeaderProps {
  title: string;
  subtitle?: string;
  actions?: React.ReactNode;
  activeCount?: number;
  healthStatus?: 'NOMINAL' | 'ELEVATED' | 'CRITICAL';
}

export const WorkspaceHeader: React.FC<WorkspaceHeaderProps> = ({
  title,
  subtitle,
  actions,
  activeCount,
  healthStatus = 'NOMINAL',
}) => {
  const getBadgeStyle = () => {
    switch (healthStatus) {
      case 'CRITICAL':
        return 'bg-rose-500/10 border-rose-500/30 text-rose-400';
      case 'ELEVATED':
        return 'bg-amber-500/10 border-amber-500/30 text-amber-400';
      default:
        return 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400';
    }
  };

  return (
    <div className="bg-[#080d1a]/80 backdrop-blur-md border-b border-slate-800/80 px-6 py-4 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
      <div>
        <Breadcrumbs />
        <div className="flex items-center gap-3 mt-1">
          <h1 className="text-xl font-bold font-mono tracking-tight text-slate-100 flex items-center gap-2">
            {title}
            {activeCount !== undefined && (
              <span className="text-xs font-mono px-2 py-0.5 rounded-full bg-slate-800 border border-slate-700 text-cyan-400">
                {activeCount} active
              </span>
            )}
          </h1>
          <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded border uppercase tracking-wider ${getBadgeStyle()}`}>
            ● {healthStatus}
          </span>
        </div>
        {subtitle && <p className="text-xs text-slate-400 mt-0.5 font-sans">{subtitle}</p>}
      </div>

      {actions && <div className="flex items-center gap-2">{actions}</div>}
    </div>
  );
};
