import React from 'react';
import { Button } from './Button';

export interface ErrorStateProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = 'System Interface Error',
  message = 'An unexpected layout or state error occurred while rendering this workspace panel.',
  onRetry,
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-10 text-center border border-accent-rose/30 bg-accent-rose/10 rounded-lg my-4">
      <div className="w-10 h-10 rounded-full bg-accent-rose/20 text-accent-rose flex items-center justify-center font-bold mb-3">
        ⚠
      </div>
      <h4 className="text-base font-semibold text-rose-200">{title}</h4>
      <p className="text-xs text-rose-300/80 max-w-md mt-1 mb-4">{message}</p>
      {onRetry && (
        <Button variant="danger" size="sm" onClick={onRetry}>
          Retry Connection
        </Button>
      )}
    </div>
  );
};
