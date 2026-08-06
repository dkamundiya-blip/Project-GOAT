/**
 * Project GOAT v1.0 — Institutional High-Performance Data Grid Component
 * Step 1.4 Presentation Layer Upgrade
 */

import React, { useState, useMemo } from 'react';
import { usePipelineStore } from '../../stores/pipelineStore';

export interface DataGridColumn<T> {
  key: keyof T | string;
  header: string;
  width?: string;
  sortable?: boolean;
  filterable?: boolean;
  render?: (row: T) => React.ReactNode;
}

export interface DataGridWidgetProps<T extends Record<string, any>> {
  title?: string;
  data: T[];
  columns: DataGridColumn<T>[];
  canonicalIdKey?: keyof T;
  onRowClick?: (row: T) => void;
  pageSize?: number;
}

export function DataGridWidget<T extends Record<string, any>>({
  title = 'INSTITUTIONAL DATA GRID',
  data,
  columns,
  canonicalIdKey = 'canonicalId' as keyof T,
  onRowClick,
  pageSize: initialPageSize = 10,
}: DataGridWidgetProps<T>) {
  const [searchQuery, setSearchQuery] = useState('');
  const [sortColumn, setSortColumn] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(initialPageSize);
  const [selectedRows, setSelectedRows] = useState<Set<string>>(new Set());
  const [contextMenu, setContextMenu] = useState<{ x: number; y: number; row: T } | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const { inspectEntityById } = usePipelineStore();

  // Filter Data
  const filteredData = useMemo(() => {
    if (!searchQuery.trim()) return data;
    const query = searchQuery.toLowerCase();
    return data.filter((row) =>
      Object.values(row).some((val) => String(val).toLowerCase().includes(query))
    );
  }, [data, searchQuery]);

  // Sort Data
  const sortedData = useMemo(() => {
    if (!sortColumn) return filteredData;
    return [...filteredData].sort((a, b) => {
      const aVal = a[sortColumn];
      const bVal = b[sortColumn];
      if (aVal < bVal) return sortDirection === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });
  }, [filteredData, sortColumn, sortDirection]);

  // Paginate Data
  const totalPages = Math.ceil(sortedData.length / pageSize) || 1;
  const paginatedData = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return sortedData.slice(start, start + pageSize);
  }, [sortedData, currentPage, pageSize]);

  const handleSort = (key: string) => {
    if (sortColumn === key) {
      setSortDirection((prev) => (prev === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortColumn(key);
      setSortDirection('asc');
    }
  };

  const toggleRowSelect = (id: string) => {
    setSelectedRows((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const handleCopy = (text: string, e: React.MouseEvent) => {
    e.stopPropagation();
    navigator.clipboard.writeText(text);
    setCopiedId(text);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleContextMenu = (e: React.MouseEvent, row: T) => {
    e.preventDefault();
    setContextMenu({ x: e.clientX, y: e.clientY, row });
  };

  return (
    <div className="bg-[#0b101b]/90 border border-slate-800/80 rounded-xl shadow-xl overflow-hidden font-mono text-xs">
      {/* Header Bar */}
      <div className="p-4 bg-[#06090e]/80 border-b border-slate-800/80 flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <span className="text-cyan-400 font-bold text-sm">📊 {title}</span>
          <span className="text-[10px] text-slate-400 px-2 py-0.5 rounded bg-slate-900 border border-slate-800">
            {sortedData.length} records
          </span>
        </div>

        {/* Controls */}
        <div className="flex items-center gap-3">
          {/* Search Box */}
          <div className="relative">
            <input
              type="text"
              placeholder="Search in grid..."
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setCurrentPage(1);
              }}
              className="bg-slate-900 border border-slate-800 focus:border-cyan-500 text-slate-100 text-xs px-3 py-1.5 rounded-md w-48 focus:outline-none transition-colors"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute right-2 top-1.2 text-slate-500 hover:text-slate-300"
              >
                ✕
              </button>
            )}
          </div>

          {/* Page Size Selector */}
          <select
            value={pageSize}
            onChange={(e) => {
              setPageSize(Number(e.target.value));
              setCurrentPage(1);
            }}
            className="bg-slate-900 border border-slate-800 text-slate-300 text-xs px-2 py-1.5 rounded-md focus:outline-none"
          >
            <option value={10}>10 / page</option>
            <option value={25}>25 / page</option>
            <option value={50}>50 / page</option>
            <option value={100}>100 / page</option>
          </select>
        </div>
      </div>

      {/* Main Table */}
      <div className="overflow-x-auto max-h-[500px]">
        <table className="w-full text-left border-collapse">
          <thead className="bg-[#080d1a] border-b border-slate-800 text-slate-400 font-bold sticky top-0 z-10">
            <tr>
              <th className="p-3 w-10 text-center">
                <input
                  type="checkbox"
                  onChange={(e) => {
                    if (e.target.checked) {
                      const allIds = paginatedData.map((r) => String(r[canonicalIdKey] || Math.random()));
                      setSelectedRows(new Set(allIds));
                    } else {
                      setSelectedRows(new Set());
                    }
                  }}
                  className="rounded bg-slate-900 border-slate-800 text-cyan-500 focus:ring-0"
                />
              </th>
              {columns.map((col) => (
                <th
                  key={String(col.key)}
                  onClick={() => col.sortable !== false && handleSort(String(col.key))}
                  className={`p-3 select-none ${col.sortable !== false ? 'cursor-pointer hover:text-cyan-400' : ''}`}
                  style={{ width: col.width }}
                >
                  <div className="flex items-center gap-1">
                    <span>{col.header}</span>
                    {col.sortable !== false && sortColumn === String(col.key) && (
                      <span className="text-cyan-400">{sortDirection === 'asc' ? '▲' : '▼'}</span>
                    )}
                  </div>
                </th>
              ))}
              <th className="p-3 text-right">ACTIONS</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {paginatedData.length === 0 ? (
              <tr>
                <td colSpan={columns.length + 2} className="p-8 text-center text-slate-500">
                  NO RECORDS FOUND IN DATA GRID
                </td>
              </tr>
            ) : (
              paginatedData.map((row, idx) => {
                const rowId = String(row[canonicalIdKey] || idx);
                const isSelected = selectedRows.has(rowId);

                return (
                  <tr
                    key={rowId}
                    onClick={() => onRowClick && onRowClick(row)}
                    onContextMenu={(e) => handleContextMenu(e, row)}
                    className={`group hover:bg-slate-800/60 transition-colors ${
                      isSelected ? 'bg-cyan-950/40' : 'bg-transparent'
                    }`}
                  >
                    <td className="p-3 text-center" onClick={(e) => e.stopPropagation()}>
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => toggleRowSelect(rowId)}
                        className="rounded bg-slate-900 border-slate-800 text-cyan-500"
                      />
                    </td>
                    {columns.map((col) => (
                      <td key={String(col.key)} className="p-3 text-slate-200">
                        {col.render ? (
                          col.render(row)
                        ) : String(col.key) === String(canonicalIdKey) ? (
                          <div className="flex items-center gap-1.5 font-bold text-cyan-400">
                            <span>{String(row[col.key])}</span>
                            <button
                              onClick={(e) => handleCopy(String(row[col.key]), e)}
                              className="text-[10px] text-slate-500 hover:text-cyan-300"
                              title="Copy Canonical ID"
                            >
                              {copiedId === String(row[col.key]) ? '✓' : '📋'}
                            </button>
                          </div>
                        ) : (
                          String(row[col.key] ?? '-')
                        )}
                      </td>
                    ))}
                    <td className="p-3 text-right" onClick={(e) => e.stopPropagation()}>
                      <button
                        onClick={() => inspectEntityById(rowId)}
                        className="px-2 py-1 rounded bg-slate-800 hover:bg-cyan-900 text-slate-300 hover:text-cyan-300 border border-slate-700 transition-colors"
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Footer */}
      <div className="p-3 bg-[#06090e]/80 border-t border-slate-800/80 flex items-center justify-between text-slate-400 text-[11px]">
        <div>
          Showing page <span className="text-cyan-400 font-bold">{currentPage}</span> of{' '}
          <span className="text-slate-200">{totalPages}</span> ({selectedRows.size} selected)
        </div>
        <div className="flex items-center space-x-1">
          <button
            onClick={() => setCurrentPage(1)}
            disabled={currentPage === 1}
            className="px-2 py-1 rounded bg-slate-900 border border-slate-800 disabled:opacity-40 hover:bg-slate-800"
          >
            « First
          </button>
          <button
            onClick={() => setCurrentPage((p) => Math.max(p - 1, 1))}
            disabled={currentPage === 1}
            className="px-2 py-1 rounded bg-slate-900 border border-slate-800 disabled:opacity-40 hover:bg-slate-800"
          >
            ‹ Prev
          </button>
          <button
            onClick={() => setCurrentPage((p) => Math.min(p + 1, totalPages))}
            disabled={currentPage === totalPages}
            className="px-2 py-1 rounded bg-slate-900 border border-slate-800 disabled:opacity-40 hover:bg-slate-800"
          >
            Next ›
          </button>
          <button
            onClick={() => setCurrentPage(totalPages)}
            disabled={currentPage === totalPages}
            className="px-2 py-1 rounded bg-slate-900 border border-slate-800 disabled:opacity-40 hover:bg-slate-800"
          >
            Last »
          </button>
        </div>
      </div>

      {/* Context Menu Popup */}
      {contextMenu && (
        <div
          className="fixed bg-[#0e1626] border border-cyan-500/60 p-2 rounded-lg shadow-2xl z-50 font-mono text-xs w-48 space-y-1"
          style={{ top: contextMenu.y, left: contextMenu.x }}
          onClick={() => setContextMenu(null)}
        >
          <div className="text-[10px] text-slate-500 font-bold border-b border-slate-800 pb-1 mb-1">
            CONTEXT ACTIONS
          </div>
          <button
            onClick={() => inspectEntityById(String(contextMenu.row[canonicalIdKey] || ''))}
            className="w-full text-left px-2 py-1 rounded hover:bg-slate-800 text-cyan-300"
          >
            🔍 Inspect Entity
          </button>
          <button
            onClick={() => navigator.clipboard.writeText(String(contextMenu.row[canonicalIdKey] || ''))}
            className="w-full text-left px-2 py-1 rounded hover:bg-slate-800 text-slate-300"
          >
            📋 Copy ID
          </button>
          <button className="w-full text-left px-2 py-1 rounded hover:bg-slate-800 text-slate-300">
            🔄 Replay Lineage
          </button>
        </div>
      )}
    </div>
  );
}
