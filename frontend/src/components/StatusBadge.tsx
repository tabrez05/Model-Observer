import type { RunStatus } from '../types';

const MAP: Record<RunStatus, { label: string; cls: string }> = {
  running:   { label: '● Running',   cls: 'bg-blue-900/60  text-blue-300' },
  completed: { label: '✓ Completed', cls: 'bg-green-900/60 text-green-300' },
  failed:    { label: '✕ Failed',    cls: 'bg-red-900/60   text-red-300' },
  cancelled: { label: '○ Cancelled', cls: 'bg-gray-800     text-gray-400' },
};

export default function StatusBadge({ status }: { status: RunStatus }) {
  const { label, cls } = MAP[status] ?? MAP.cancelled;
  return <span className={`badge ${cls}`}>{label}</span>;
}
