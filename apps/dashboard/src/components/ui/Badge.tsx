import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'primary' | 'success' | 'warning' | 'danger' | 'purple' | 'muted';
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'primary',
  className,
  ...props
}) => {
  const variants = {
    primary: 'bg-primary/20 text-primary border-primary/30',
    success: 'bg-accent-emerald/20 text-accent-emerald border-accent-emerald/30',
    warning: 'bg-accent-amber/20 text-accent-amber border-accent-amber/30',
    danger: 'bg-accent-rose/20 text-accent-rose border-accent-rose/30',
    purple: 'bg-accent-purple/20 text-accent-purple border-accent-purple/30',
    muted: 'bg-slate-800 text-slate-400 border-slate-700',
  };

  return (
    <span
      className={twMerge(
        clsx(
          'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border uppercase tracking-wider',
          variants[variant],
          className
        )
      )}
      {...props}
    >
      {children}
    </span>
  );
};
