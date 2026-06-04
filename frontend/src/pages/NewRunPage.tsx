import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createRun } from '../api';

export default function NewRunPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    name: '',
    model_type: '',
    dataset: '',
    tags: '',
    notes: '',
    hyperparams: '{}',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const set = (k: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) =>
    setForm(f => ({ ...f, [k]: e.target.value }));

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    let hyperparams: Record<string, unknown> = {};
    try {
      hyperparams = JSON.parse(form.hyperparams);
    } catch {
      setError('Hyperparameters must be valid JSON.');
      return;
    }
    setLoading(true);
    try {
      const run = await createRun({
        name: form.name,
        model_type: form.model_type,
        dataset: form.dataset,
        tags: form.tags.split(',').map(t => t.trim()).filter(Boolean),
        notes: form.notes || null,
        hyperparams,
        status: 'running',
      });
      navigate(`/runs/${run.id}`);
    } catch {
      setError('Failed to create run. Is the API running?');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-xl space-y-6">
      <h1 className="text-xl font-bold text-white">New Experiment Run</h1>

      <form onSubmit={submit} className="card space-y-5">
        <div className="space-y-1.5">
          <label className="text-xs text-gray-400 uppercase tracking-wide">Run Name *</label>
          <input required className="input w-full" placeholder="e.g. SVM-Banking77-v2" value={form.name} onChange={set('name')} />
        </div>
        <div className="space-y-1.5">
          <label className="text-xs text-gray-400 uppercase tracking-wide">Model Type *</label>
          <input required className="input w-full" placeholder="e.g. SVM, MLP, BERT" value={form.model_type} onChange={set('model_type')} />
        </div>
        <div className="space-y-1.5">
          <label className="text-xs text-gray-400 uppercase tracking-wide">Dataset *</label>
          <input required className="input w-full" placeholder="e.g. Banking77" value={form.dataset} onChange={set('dataset')} />
        </div>
        <div className="space-y-1.5">
          <label className="text-xs text-gray-400 uppercase tracking-wide">Tags (comma-separated)</label>
          <input className="input w-full" placeholder="e.g. baseline, tfidf, no-aug" value={form.tags} onChange={set('tags')} />
        </div>
        <div className="space-y-1.5">
          <label className="text-xs text-gray-400 uppercase tracking-wide">Hyperparameters (JSON)</label>
          <textarea
            className="input w-full font-mono text-xs resize-none"
            rows={5}
            value={form.hyperparams}
            onChange={set('hyperparams')}
          />
        </div>
        <div className="space-y-1.5">
          <label className="text-xs text-gray-400 uppercase tracking-wide">Notes</label>
          <textarea className="input w-full resize-none" rows={3} placeholder="Optional notes…" value={form.notes} onChange={set('notes')} />
        </div>
        {error && <p className="text-red-400 text-sm">{error}</p>}
        <button type="submit" className="btn-primary w-full justify-center" disabled={loading}>
          {loading ? 'Creating…' : 'Create Run'}
        </button>
      </form>
    </div>
  );
}
