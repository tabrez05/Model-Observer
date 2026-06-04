interface Props {
  label: string;
  value: number | null | undefined;
  unit?: string;
  highlight?: boolean;
}

export default function MetricCard({ label, value, unit = '', highlight }: Props) {
  const display =
    value == null ? '—' : Number.isInteger(value) ? value.toString() : value.toFixed(4);
  return (
    <div className={`card flex flex-col gap-1 ${highlight ? 'border-brand-600' : ''}`}>
      <span className="text-xs text-gray-500 uppercase tracking-wide">{label}</span>
      <span className="text-2xl font-bold text-white">
        {display}
        {value != null && unit && <span className="text-sm text-gray-400 ml-1">{unit}</span>}
      </span>
    </div>
  );
}
