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
import type { MetricSnapshot, Run } from '../types';

const COLORS = ['#3b82f6', '#f59e0b', '#10b981', '#ef4444', '#8b5cf6'];

interface SeriesData {
  run: Run;
  snapshots: MetricSnapshot[];
}

interface Props {
  series: SeriesData[];
  metric: string;
}

export default function CompareChart({ series, metric }: Props) {
  // Align all runs by step
  const allSteps = Array.from(
    new Set(series.flatMap(s => s.snapshots.map(m => m.step)))
  ).sort((a, b) => a - b);

  const data = allSteps.map(step => {
    const row: Record<string, number | string> = { step };
    series.forEach(({ run, snapshots }) => {
      const snap = snapshots.find(s => s.step === step);
      if (snap && metric in snap.metrics) {
        row[run.name] = snap.metrics[metric];
      }
    });
    return row;
  });

  return (
    <ResponsiveContainer width="100%" height={280}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
        <XAxis dataKey="step" stroke="#4b5563" tick={{ fill: '#9ca3af', fontSize: 11 }} />
        <YAxis stroke="#4b5563" tick={{ fill: '#9ca3af', fontSize: 11 }} width={55} />
        <Tooltip
          contentStyle={{ background: '#111827', border: '1px solid #374151', borderRadius: 8 }}
          labelStyle={{ color: '#d1d5db' }}
          itemStyle={{ color: '#9ca3af' }}
        />
        <Legend wrapperStyle={{ fontSize: 12, color: '#9ca3af' }} />
        {series.map(({ run }, i) => (
          <Line
            key={run.id}
            type="monotone"
            dataKey={run.name}
            stroke={COLORS[i % COLORS.length]}
            dot={false}
            strokeWidth={2}
            isAnimationActive={false}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}
