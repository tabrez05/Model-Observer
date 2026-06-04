import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { getRuns } from '../api';
import StatusBadge from '../components/StatusBadge';
import { useCompareStore } from '../store';
import type { Run } from '../types';

function fmt(iso: string) {
  return new Date(iso).toLocaleString(undefined, { dateStyle: 'short', timeStyle: 'short' });
}

function dur(s: number | null) {
  if (s == null) return '—';
  if (s < 60) return `${s.toFixed(0)}s`;
  return `${(s / 60).toFixed(1)}m`;
}

export default function RunsListPage() {
  const [status, setStatus] = useState('');
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const PAGE_SIZE = 20;

  const { data, isLoading, isError } = useQuery({
    queryKey: ['runs', status, page],
    queryFn: () => getRuns({ status: status || undefined, page, page_size: PAGE_SIZE }),
    refetchInterval: 5000,
  });

  const { selectedIds, toggle } = useCompareStore();

  const rows = (data?.items ?? []).filter(r =>
    search === '' ||
    r.name.toLowerCase().includes(search.toLowerCase()) ||
    r.model_type.toLowerCase().includes(search.toLowerCase()) ||
    r.dataset.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-white">Experiment Runs</h1>
        <Link to="/new" className="btn-primary text-sm">+ New Run</Link>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-3 flex-wrap">
        <input
          className="input w-60"
          placeholder="Search name / model / dataset…"
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
        <select
          className="input"
          value={status}
          onChange={e => { setStatus(e.target.value); setPage(1); }}
        >
          <option value="">All statuses</option>
          <option value="running">Running</option>
          <option value="completed">Completed</option>
          <option value="failed">Failed</option>
          <option value="cancelled">Cancelled</option>
        </select>
      </div>

      {isLoading && <div className="text-gray-500 text-sm">Loading…</div>}
      {isError && <div className="text-red-400 text-sm">Failed to load runs.</div>}

      {!isLoading && rows.length === 0 && (
        <div className="card text-center text-gray-500 py-16">
          No runs found.{' '}
          <Link to="/new" className="text-brand-400 hover:underline">Create one →</Link>
        </div>
      )}

      {rows.length > 0 && (
        <div className="overflow-x-auto rounded-xl border border-gray-800">
          <table className="w-full text-sm">
            <thead className="bg-gray-900 text-gray-400 text-xs uppercase tracking-wide">
              <tr>
                <th className="px-3 py-3 w-8" />
                <th className="px-3 py-3 text-left">Name</th>
                <th className="px-3 py-3 text-left">Model</th>
                <th className="px-3 py-3 text-left">Dataset</th>
                <th className="px-3 py-3 text-left">Status</th>
                <th className="px-3 py-3 text-right">F1 (macro)</th>
                <th className="px-3 py-3 text-right">Acc</th>
                <th className="px-3 py-3 text-right">Duration</th>
                <th className="px-3 py-3 text-left">Created</th>
                <th className="px-3 py-3 text-left">Tags</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800">
              {rows.map((run: Run) => (
                <tr
                  key={run.id}
                  className="hover:bg-gray-800/50 transition-colors"
                >
                  <td className="px-3 py-3">
                    <input
                      type="checkbox"
                      checked={selectedIds.includes(run.id)}
                      onChange={() => toggle(run.id)}
                      className="accent-brand-500"
                    />
                  </td>
                  <td className="px-3 py-3">
                    <Link to={`/runs/${run.id}`} className="text-brand-400 hover:underline font-medium">
                      {run.name}
                    </Link>
                  </td>
                  <td className="px-3 py-3 text-gray-300">{run.model_type}</td>
                  <td className="px-3 py-3 text-gray-400">{run.dataset}</td>
                  <td className="px-3 py-3"><StatusBadge status={run.status} /></td>
                  <td className="px-3 py-3 text-right text-gray-200 tabular-nums">
                    {(run.final_metrics?.f1_macro ?? run.final_metrics?.macro_f1) != null
                      ? ((run.final_metrics?.f1_macro ?? run.final_metrics?.macro_f1) as number).toFixed(4)
                      : '—'}
                  </td>
                  <td className="px-3 py-3 text-right text-gray-200 tabular-nums">
                    {run.final_metrics?.accuracy != null
                      ? (run.final_metrics.accuracy * 100).toFixed(1) + '%'
                      : run.final_metrics?.val_accuracy != null
                      ? (run.final_metrics.val_accuracy * 100).toFixed(1) + '%'
                      : '—'}
                  </td>
                  <td className="px-3 py-3 text-right text-gray-400 tabular-nums">
                    {dur(run.duration_seconds)}
                  </td>
                  <td className="px-3 py-3 text-gray-500">{fmt(run.created_at)}</td>
                  <td className="px-3 py-3">
                    <div className="flex flex-wrap gap-1">
                      {run.tags.map(t => (
                        <span key={t} className="badge bg-gray-800 text-gray-400">{t}</span>
                      ))}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Pagination */}
      {data && data.total > PAGE_SIZE && (
        <div className="flex items-center justify-between text-sm text-gray-400">
          <span>{data.total} total runs</span>
          <div className="flex gap-2">
            <button className="btn-ghost" disabled={page <= 1} onClick={() => setPage(p => p - 1)}>← Prev</button>
            <span className="px-2 py-1">Page {page}</span>
            <button className="btn-ghost" disabled={page * PAGE_SIZE >= data.total} onClick={() => setPage(p => p + 1)}>Next →</button>
          </div>
        </div>
      )}
    </div>
  );
}
