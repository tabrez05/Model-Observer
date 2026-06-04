export type RunStatus = 'running' | 'completed' | 'failed' | 'cancelled';

export interface Run {
  id: string;
  name: string;
  model_type: string;
  dataset: string;
  status: RunStatus;
  hyperparams: Record<string, unknown>;
  final_metrics: Record<string, number> | null;
  tags: string[];
  notes: string | null;
  duration_seconds: number | null;
  created_at: string;
  completed_at: string | null;
}

export interface RunListResponse {
  items: Run[];
  total: number;
  page: number;
  page_size: number;
}

export interface MetricSnapshot {
  id: string;
  run_id: string;
  step: number;
  metrics: Record<string, number>;
  recorded_at: string;
}
