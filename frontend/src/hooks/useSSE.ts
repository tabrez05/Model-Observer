import { useEffect, useRef, useState } from 'react';
import type { MetricSnapshot } from '../types';

export function useSSE(runId: string | null) {
  const [snapshots, setSnapshots] = useState<MetricSnapshot[]>([]);
  const [connected, setConnected] = useState(false);
  const esRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (!runId) return;

    const es = new EventSource(`/api/v1/runs/${runId}/stream`);
    esRef.current = es;

    es.onopen = () => setConnected(true);

    es.addEventListener('metric', (e: MessageEvent) => {
      try {
        const snap: MetricSnapshot = JSON.parse(e.data);
        setSnapshots(prev => {
          const exists = prev.some(s => s.step === snap.step);
          if (exists) return prev.map(s => (s.step === snap.step ? snap : s));
          return [...prev, snap].sort((a, b) => a.step - b.step);
        });
      } catch { /* ignore parse errors */ }
    });

    es.onerror = () => setConnected(false);

    return () => {
      es.close();
      setConnected(false);
    };
  }, [runId]);

  return { snapshots, connected };
}
