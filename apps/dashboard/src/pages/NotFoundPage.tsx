import React from 'react';
import { Button } from '../components/ui/Button';
import { useNavigate } from 'react-router-dom';

export const NotFoundPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
      <h1 className="text-6xl font-extrabold text-primary font-mono">404</h1>
      <h2 className="text-xl font-bold text-slate-100 mt-2">Route Not Found</h2>
      <p className="text-sm text-slate-400 max-w-md mt-1 mb-6">
        The requested control room route does not exist or has been relocated in Version 1.0.
      </p>
      <Button variant="primary" onClick={() => navigate('/')}>
        Return to Overview Dashboard
      </Button>
    </div>
  );
};
export default NotFoundPage;
