import React from 'react';
import { useLocation, Link } from 'react-router-dom';

export const Breadcrumbs: React.FC = () => {
  const location = useLocation();
  const pathnames = location.pathname.split('/').filter((x) => x);

  const formatBreadcrumb = (name: string) => {
    return name
      .replace(/-/g, ' ')
      .replace(/([A-Z])/g, ' $1')
      .trim()
      .toUpperCase();
  };

  return (
    <nav aria-label="Breadcrumb" className="flex items-center text-xs text-slate-400 font-mono">
      <Link to="/" className="hover:text-cyan-400 transition-colors flex items-center gap-1">
        <span className="text-cyan-500">◆</span> WORKSPACE
      </Link>
      {pathnames.map((value, index) => {
        const to = `/${pathnames.slice(0, index + 1).join('/')}`;
        const isLast = index === pathnames.length - 1;

        return (
          <React.Fragment key={to}>
            <span className="mx-2 text-slate-600">/</span>
            {isLast ? (
              <span className="text-cyan-400 font-semibold tracking-wider">{formatBreadcrumb(value)}</span>
            ) : (
              <Link to={to} className="hover:text-slate-200 transition-colors">
                {formatBreadcrumb(value)}
              </Link>
            )}
          </React.Fragment>
        );
      })}
    </nav>
  );
};
