import React from 'react';

export interface KPICardProps {
  icon: string;
  title: string;
  value: string | number;
  subValue?: string;
  trend?: {
    value: string;
    isPositive?: boolean;
    label?: string;
  };
  tooltip?: string;
  isLoading?: boolean;
  statusBadge?: {
    text: string;
    variant?: 'nominal' | 'elevated' | 'critical' | 'active' | 'neutral';
  };
  sparklineData?: number[];
  onClick?: () => void;
}

export const KPICard: React.FC<KPICardProps> = ({
  icon,
  title,
  value,
  subValue,
  trend,
  tooltip,
  isLoading = false,
  statusBadge,
  sparklineData,
  onClick,
}) => {
  if (isLoading) {
    return (
      <div className="bg-[#0b101b]/80 border border-slate-800/80 p-4 rounded-xl shadow-lg animate-pulse space-y-3">
        <div className="flex justify-between items-center">
          <div className="h-4 w-24 bg-slate-800 rounded" />
          <div className="h-6 w-6 bg-slate-800 rounded-full" />
        </div>
        <div className="h-8 w-36 bg-slate-800 rounded" />
        <div className="h-3 w-20 bg-slate-800 rounded" />
      </div>
    );
  }

  const getBadgeClass = (variant = 'neutral') => {
    switch (variant) {
      case 'nominal':
        return 'bg-emerald-950/80 text-emerald-400 border-emerald-800/60';
      case 'elevated':
        return 'bg-amber-950/80 text-amber-400 border-amber-800/60';
      case 'critical':
        return 'bg-rose-950/80 text-rose-400 border-rose-800/60';
      case 'active':
        return 'bg-cyan-950/80 text-cyan-400 border-cyan-800/60';
      default:
        return 'bg-slate-800 text-slate-300 border-slate-700';
    }
  };

  return (
    <div
      onClick={onClick}
      title={tooltip}
      className={`group relative bg-[#0b101b]/80 hover:bg-[#121a2d]/90 backdrop-blur-md border border-slate-800/80 hover:border-cyan-500/40 p-4 rounded-xl shadow-lg transition-all duration-300 ${
        onClick ? 'cursor-pointer hover:shadow-cyan-500/10' : ''
      }`}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className="text-lg p-1.5 rounded-lg bg-slate-900 border border-slate-800/80 group-hover:border-cyan-500/30 transition-colors">
            {icon}
          </span>
          <span className="text-xs font-mono font-semibold text-slate-400 uppercase tracking-wider">
            {title}
          </span>
        </div>
        {statusBadge && (
          <span
            className={`text-[9.5px] font-mono font-bold px-2 py-0.5 rounded border uppercase tracking-wider ${getBadgeClass(
              statusBadge.variant
            )}`}
          >
            {statusBadge.text}
          </span>
        )}
      </div>

      {/* Main Value */}
      <div className="flex items-baseline justify-between mt-1">
        <div>
          <div className="text-2xl font-bold font-mono tracking-tight text-slate-100 group-hover:text-cyan-300 transition-colors">
            {value}
          </div>
          {subValue && <div className="text-[11px] font-mono text-slate-400 mt-0.5">{subValue}</div>}
        </div>

        {/* Sparkline Mini Preview */}
        {sparklineData && sparklineData.length > 1 && (
          <div className="w-16 h-8 flex items-end gap-1">
            {sparklineData.map((val, idx) => {
              const max = Math.max(...sparklineData, 1);
              const heightPct = Math.max((val / max) * 100, 10);
              return (
                <div
                  key={idx}
                  className="flex-1 bg-cyan-500/40 group-hover:bg-cyan-400 rounded-t transition-all"
                  style={{ height: `${heightPct}%` }}
                />
              );
            })}
          </div>
        )}
      </div>

      {/* Trend indicator */}
      {trend && (
        <div className="flex items-center gap-1.5 mt-2 text-xs font-mono">
          <span
            className={`font-semibold ${
              trend.isPositive !== false ? 'text-emerald-400' : 'text-rose-400'
            }`}
          >
            {trend.isPositive !== false ? '▲' : '▼'} {trend.value}
          </span>
          {trend.label && <span className="text-slate-500 text-[10.5px]">{trend.label}</span>}
        </div>
      )}
    </div>
  );
};
