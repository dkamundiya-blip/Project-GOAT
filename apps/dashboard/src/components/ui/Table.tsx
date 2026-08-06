import React from 'react';

export interface Column<T> {
  key: string;
  header: string;
  render?: (row: T) => React.ReactNode;
}

export interface TableProps<T> {
  columns: Column<T>[];
  data: T[];
  emptyText?: string;
}

export function Table<T extends Record<string, unknown>>({
  columns,
  data,
  emptyText = 'No data available',
}: TableProps<T>) {
  return (
    <div className="w-full overflow-x-auto border border-border rounded-lg bg-surface">
      <table className="w-full text-left border-collapse text-sm">
        <thead>
          <tr className="border-b border-border bg-surface-elevated text-slate-400 text-xs font-semibold uppercase tracking-wider">
            {columns.map((col) => (
              <th key={col.key} className="p-3">
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-border text-slate-200">
          {data.length === 0 ? (
            <tr>
              <td colSpan={columns.length} className="p-6 text-center text-slate-500">
                {emptyText}
              </td>
            </tr>
          ) : (
            data.map((row, idx) => (
              <tr key={idx} className="hover:bg-slate-800/50 transition-colors">
                {columns.map((col) => (
                  <td key={col.key} className="p-3">
                    {col.render ? col.render(row) : String(row[col.key] ?? '')}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
