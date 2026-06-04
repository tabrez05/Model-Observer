import { useMemo, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getRun, getMetrics } from '../api';
import CompareChart from '../components/CompareChart';
import StatusBadge from '../components/StatusBadge';

const COLORS = ['#3b82f6', '#f59e0b', '#10b981', '#ef4444', '#8b5cf6'];

function useRunData(ids: string[]) {
  const runs = useQuery({
    queryKey: ['compare-runs', ids.join(',')],
    queryFn: () => Promise.all(ids.map(id => getRun(id))),
    enabled: ids.length > 0,
  });
  const metrics = useQuery({
    queryKey: ['compare-metrics', ids.join(',')],
    queryFn: () => Promise.all(ids.map(id => getMetrics(id))),
    enabled: ids.length > 0,
  });
  return { runs, metrics };
}

export default function ComparePage() {
  const [params] = useSearchParams();
  const ids = useMemo(() => (params.get('ids') ?? '').split(',').filter(Boolean), [params]);
  const [activeMetric, setActiveMetric] = useState('loss');

  const { runs, metrics } = useRunData(ids);

  const runList = runs.data ?? [];
  const metricsList = metrics.data ?? [];

  const allMetricKeys = useMemo(() => {
    const keys = new Set<string>();
    metricsList.forEach(snaps => snaps.forEach(s => Object.keys(s.metrics).forEach(k => keys.add(k))));
    return Array.from(keys).sort();
  }, [metricsList]);

  if (ids.length === 0) {
    return (
      <div className="card text-center text-gray-500 py-20">
        Select runs from the{' '}
        <a href="/" className="text-brand-400 hover:underline">Runs list</a>{' '}
        to compare them here.
      </div>
    );
  }

  if (runs.isLoading || metrics.isLoading) {
    return <div className="text-gray-500 text-sm">Loading comparison data…</div>;
  }

  const series = runList.map((run, i) => ({ run, snapshots: metricsList[i] ?? [] }));

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-bold text-white">Compare Runs</h1>

      {/* Run header cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {runList.map((run, i) => (
          <div key={run.id} className="card border-l-4" style={{ borderLeftColor: COLORS[i % COLORS.length] }}>
            <div className="flex items-start justify-between gap-2">
              <div>
                <p className="font-semibold text-white text-sm">{run.name}</p>
                <p className="text-xs text-gray-500 mt-0.5">{run.model_type} · {run.dataset}</p>
              </div>
              <StatusBadge status={run.status} />
            </div>
            {run.final_metrics && (
              <div className="mt-3 flex gap-4 text-xs">
                {run.final_metrics.f1_macro != null && (
                  <span className="text-gray-400">F1 <span className="text-white font-mono">{run.final_metrics.f1_macro.toFixed(4)}</span></span>
                )}
                {(run.final_metrics.accuracy ?? run.final_metrics.val_accuracy) != null && (
                  <span className="text-gray-400">Acc <span className="text-white font-mono">
                    {((run.final_metrics.accuracy ?? run.final_metrics.val_accuracy) * 100).toFixed(1)}%
                  </span></span>
                )}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Metric selector + chart */}
      {allMetricKeys.length > 0 && (
        <div className="card space-y-4">
          <div className="flex items-center gap-3 flex-wrap">
            <span className="text-sm text-gray-400">Metric:</span>
            {allMetricKeys.map(k => (
              <button
                key={k}
                className={`text-xs px-2.5 py-1 rounded-full border transition-colors ${
                  activeMetric === k
                    ? 'border-brand-500 bg-brand-900/40 text-brand-300'
                    : 'border-gray-700 text-gray-400 hover:border-gray-500'
                }`}
                onClick={() => setActiveMetric(k)}
              >
                {k}
              </button>
            ))}
          </div>
          <CompareChart series={series} metric={activeMetric} />
        </div>
      )}

      {/* Final metrics comparison table */}
      <div className="overflow-x-auto rounded-xl border border-gray-800">
        <table className="w-full text-sm">
          <thead className="bg-gray-900 text-gray-400 text-xs uppercase tracking-wide">
            <tr>
              <th className="px-4 py-3 text-left">Metric</th>
              {runList.map((r, i) => (
                <th
                  key={r.id}
                  className="px-4 py-3 text-right"
                  style={{ color: COLORS[i % COLORS.length] }}
                >
                  {r.name}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800">
            {Array.from(
              new Set(runList.flatMap(r => Object.keys(r.final_metrics ?? {})))
            ).map(key => (
              <tr key={key} className="hover:bg-gray-800/40">
                <td className="px-4 py-2.5 text-gray-400 font-mono text-xs">{key}</td>
                {runList.map(r => {
                  const val = r.final_metrics?.[key];
                  return (
                    <td key={r.id} className="px-4 py-2.5 text-right text-gray-200 tabular-nums font-mono text-xs">
                      {val == null ? '—' : typeof val === 'number' ? val.toFixed(4) : String(val)}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
