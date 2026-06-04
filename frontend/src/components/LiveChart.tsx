import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import type { MetricSnapshot } from '../types';

const COLORS = ['#3b82f6', '#f59e0b', '#10b981', '#ef4444', '#8b5cf6'];

interface Props {
  snapshots: MetricSnapshot[];
  title?: string;
  connected?: boolean;
}

export default function LiveChart({ snapshots, title = 'Training Metrics', connected }: Props) {
  if (snapshots.length === 0) {
    return (
      <div className="card flex items-center justify-center h-52 text-gray-600 text-sm">
        No metric data yet.
      </div>
    );
  }

  const keys = Object.keys(snapshots[0]?.metrics ?? {});
  const data = snapshots.map(s => ({ step: s.step, ...s.metrics }));

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <span className="font-medium text-gray-200">{title}</span>
        {connected !== undefined && (
          <span className={`text-xs ${connected ? 'text-green-400' : 'text-gray-600'}`}>
            {connected ? '● live' : '○ disconnected'}
          </span>
        )}
      </div>
      <ResponsiveContainer width="100%" height={260}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
          <XAxis dataKey="step" stroke="#4b5563" tick={{ fill: '#9ca3af', fontSize: 11 }} label={{ value: 'Step / Epoch', position: 'insideBottom', offset: -2, fill: '#6b7280', fontSize: 11 }} />
          <YAxis stroke="#4b5563" tick={{ fill: '#9ca3af', fontSize: 11 }} width={50} />
          <Tooltip
            contentStyle={{ background: '#111827', border: '1px solid #374151', borderRadius: 8 }}
            labelStyle={{ color: '#d1d5db' }}
            itemStyle={{ color: '#9ca3af' }}
          />
          <Legend wrapperStyle={{ fontSize: 12, color: '#9ca3af' }} />
          {keys.map((k, i) => (
            <Line
              key={k}
              type="monotone"
              dataKey={k}
              stroke={COLORS[i % COLORS.length]}
              dot={data.length < 60}
              strokeWidth={2}
              isAnimationActive={false}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
