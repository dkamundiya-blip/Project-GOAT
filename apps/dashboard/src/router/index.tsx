import React, { Suspense } from 'react';
import { Routes, Route } from 'react-router-dom';
import { routes } from './routes';
import { Spinner } from '../components/ui/Spinner';

export const AppRouter: React.FC = () => {
  return (
    <Suspense
      fallback={
        <div className="flex flex-col items-center justify-center min-h-[50vh] gap-3">
          <Spinner size="lg" />
          <span className="text-xs font-mono text-slate-400">Loading Control Room Workspace...</span>
        </div>
      }
    >
      <Routes>
        {routes.map((r) => {
          const Component = r.component;
          return <Route key={r.path} path={r.path} element={<Component />} />;
        })}
      </Routes>
    </Suspense>
  );
};
