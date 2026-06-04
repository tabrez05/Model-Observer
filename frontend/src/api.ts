import axios from 'axios';
import type { Run, RunListResponse, MetricSnapshot } from './types';

const http = axios.create({ baseURL: '/api/v1' });

// ─── Runs ────────────────────────────────────────────────────────────────────

export const getRuns = (params?: {
  page?: number;
  page_size?: number;
  status?: string;
  model_type?: string;
  tag?: string;
}) => http.get<RunListResponse>('/runs', { params }).then(r => r.data);

export const getRun = (id: string) =>
  http.get<Run>(`/runs/${id}`).then(r => r.data);

export const createRun = (body: Partial<Run>) =>
  http.post<Run>('/runs', body).then(r => r.data);

export const updateRun = (id: string, body: Partial<Run>) =>
  http.patch<Run>(`/runs/${id}`, body).then(r => r.data);

export const deleteRun = (id: string) =>
  http.delete(`/runs/${id}`).then(r => r.data);

// ─── Metrics ─────────────────────────────────────────────────────────────────

export const getMetrics = (runId: string) =>
  http.get<MetricSnapshot[]>(`/runs/${runId}/metrics`).then(r => r.data);

export const logMetric = (runId: string, step: number, metrics: Record<string, number>) =>
  http.post(`/runs/${runId}/metrics`, { step, metrics }).then(r => r.data);
