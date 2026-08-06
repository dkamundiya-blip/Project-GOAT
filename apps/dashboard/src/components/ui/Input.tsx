import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const Input: React.FC<InputProps> = ({ label, error, className, ...props }) => {
  return (
    <div className="w-full flex flex-col gap-1.5">
      {label && <label className="text-xs font-medium text-slate-300">{label}</label>}
      <input
        className={twMerge(
          clsx(
            'bg-surface-elevated border border-border text-slate-100 placeholder-slate-500 rounded-md px-3 py-2 text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all',
            error && 'border-accent-rose focus:ring-accent-rose',
            className
          )
        )}
        {...props}
      />
      {error && <span className="text-xs text-accent-rose">{error}</span>}
    </div>
  );
};
