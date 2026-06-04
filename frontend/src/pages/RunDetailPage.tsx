import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getRun, getMetrics } from '../api';
import StatusBadge from '../components/StatusBadge';
import MetricCard from '../components/MetricCard';
import LiveChart from '../components/LiveChart';
import { useSSE } from '../hooks/useSSE';
import type { MetricSnapshot } from '../types';

function fmt(iso: string | null) {
  if (!iso) return '—';
  return new Date(iso).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' });
}

export default function RunDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [liveEnabled, setLiveEnabled] = useState(false);

  const { data: run, isLoading } = useQuery({
    queryKey: ['run', id],
    queryFn: () => getRun(id!),
    enabled: !!id,
    refetchInterval: (query) => (query.state.data?.status === 'running' ? 3000 : false),
  });

  const { data: history = [] } = useQuery({
    queryKey: ['metrics', id],
    queryFn: () => getMetrics(id!),
    enabled: !!id,
  });

  const { snapshots: liveSnaps, connected } = useSSE(liveEnabled ? (id ?? null) : null);

  const snapshots: MetricSnapshot[] = liveEnabled && liveSnaps.length > 0 ? liveSnaps : history;

  if (isLoading) return <div className="text-gray-500 text-sm">Loading…</div>;
  if (!run) return <div className="text-red-400 text-sm">Run not found.</div>;

  const fm = run.final_metrics ?? {};

  return (
    <div className="space-y-6">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm text-gray-500">
        <Link to="/" className="hover:text-white">Runs</Link>
        <span>/</span>
        <span className="text-gray-300">{run.name}</span>
      </div>

      {/* Header */}
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-2xl font-bold text-white">{run.name}</h1>
          <p className="text-gray-400 mt-0.5">{run.model_type} · {run.dataset}</p>
        </div>
        <div className="flex items-center gap-3">
          <StatusBadge status={run.status} />
          {run.status === 'running' && (
            <button
              className={liveEnabled ? 'btn bg-blue-900/60 text-blue-300 text-xs' : 'btn-ghost text-xs'}
              onClick={() => setLiveEnabled(v => !v)}
            >
              {liveEnabled ? '● Live' : '○ Enable Live'}
            </button>
          )}
          <Link to={`/compare?ids=${id}`} className="btn-ghost text-xs">Compare →</Link>
        </div>
      </div>

      {/* Summary metrics */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
        <MetricCard label="F1 Macro" value={fm.f1_macro ?? fm.macro_f1} highlight />
        <MetricCard label="F1 Micro" value={fm.f1_micro ?? fm.micro_f1} />
        <MetricCard label="Accuracy"
          value={fm.accuracy != null ? fm.accuracy * 100 : fm.val_accuracy != null ? fm.val_accuracy * 100 : null}
          unit="%" />
        <MetricCard label="PR-AUC" value={fm.pr_auc} />
        <MetricCard label="Duration" value={run.duration_seconds} unit="s" />
      </div>

      {/* Loss / metric chart */}
      <LiveChart snapshots={snapshots} connected={liveEnabled ? connected : undefined} />

      {/* Two-column: hyperparams + final metrics */}
      <div className="grid md:grid-cols-2 gap-4">
        <div className="card">
          <h2 className="text-sm font-semibold text-gray-300 mb-3">Hyperparameters</h2>
          {Object.keys(run.hyperparams).length === 0 ? (
            <p className="text-gray-600 text-sm">None recorded.</p>
          ) : (
            <dl className="space-y-2">
              {Object.entries(run.hyperparams).map(([k, v]) => (
                <div key={k} className="flex items-center justify-between text-sm">
                  <dt className="text-gray-500">{k}</dt>
                  <dd className="text-gray-200 font-mono">{JSON.stringify(v)}</dd>
                </div>
              ))}
            </dl>
          )}
        </div>

        <div className="card">
          <h2 className="text-sm font-semibold text-gray-300 mb-3">Final Metrics</h2>
          {Object.keys(fm).length === 0 ? (
            <p className="text-gray-600 text-sm">Not yet available.</p>
          ) : (
            <dl className="space-y-2">
              {Object.entries(fm).map(([k, v]) => (
                <div key={k} className="flex items-center justify-between text-sm">
                  <dt className="text-gray-500">{k}</dt>
                  <dd className="text-gray-200 font-mono tabular-nums">
                    {typeof v === 'number' ? v.toFixed(4) : String(v)}
                  </dd>
                </div>
              ))}
            </dl>
          )}
        </div>
      </div>

      {/* Tags & notes */}
      <div className="card space-y-3">
        <div>
          <span className="text-xs text-gray-500 uppercase tracking-wide">Tags</span>
          <div className="flex flex-wrap gap-1.5 mt-1.5">
            {run.tags.length === 0 ? (
              <span className="text-gray-600 text-sm">—</span>
            ) : (
              run.tags.map(t => (
                <span key={t} className="badge bg-gray-800 text-gray-300">{t}</span>
              ))
            )}
          </div>
        </div>
        {run.notes && (
          <div>
            <span className="text-xs text-gray-500 uppercase tracking-wide">Notes</span>
            <p className="text-gray-300 text-sm mt-1 whitespace-pre-wrap">{run.notes}</p>
          </div>
        )}
        <div className="text-xs text-gray-600 flex gap-4">
          <span>Created: {fmt(run.created_at)}</span>
          {run.completed_at && <span>Completed: {fmt(run.completed_at)}</span>}
        </div>
      </div>
    </div>
  );
}
