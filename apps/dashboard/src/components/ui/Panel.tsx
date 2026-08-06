import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export interface PanelProps extends React.HTMLAttributes<HTMLDivElement> {
  header?: React.ReactNode;
  footer?: React.ReactNode;
}

export const Panel: React.FC<PanelProps> = ({ children, header, footer, className, ...props }) => {
  return (
    <div
      className={twMerge(
        clsx('flex flex-col bg-surface border border-border rounded-lg overflow-hidden', className)
      )}
      {...props}
    >
      {header && <div className="border-b border-border bg-surface-elevated p-4">{header}</div>}
      <div className="flex-1 p-4 overflow-auto">{children}</div>
      {footer && <div className="border-t border-border bg-surface-elevated p-3">{footer}</div>}
    </div>
  );
};
