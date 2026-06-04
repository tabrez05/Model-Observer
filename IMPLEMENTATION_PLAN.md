# ML Experiment Tracker — Low-Level Implementation Plan
**Tabrez Ahammed Shaik Mohammed · 012623820**
**Stack: FastAPI · PostgreSQL · Redis Streams · SSE · React · Docker · Kubernetes · GitHub Actions**

---

## Complete File Map (Every File That Will Exist)

```
ml-experiment-tracker/
│
├── backend/
│   ├── app/
│   │   ├── main.py                        ← FastAPI app factory, lifespan, CORS, routers
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── router.py              ← Aggregates all v1 routers
│   │   │       └── endpoints/
│   │   │           ├── runs.py            ← CRUD for experiment runs
│   │   │           ├── metrics.py         ← POST metric, GET history, SSE stream
│   │   │           ├── artifacts.py       ← Upload/download confusion matrices, plots
│   │   │           ├── health.py          ← GET /health (DB + Redis ping)
│   │   │           └── auth.py            ← POST /register, POST /token (Phase 6)
│   │   ├── core/
│   │   │   ├── config.py                  ← Settings (pydantic-settings, reads .env)
│   │   │   ├── security.py                ← JWT encode/decode, bcrypt hashing
│   │   │   ├── dependencies.py            ← get_db(), get_redis(), get_current_user()
│   │   │   └── exceptions.py              ← Custom HTTPExceptions + handlers
│   │   ├── db/
│   │   │   ├── session.py                 ← AsyncEngine, AsyncSessionLocal, Base
│   │   │   ├── models/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── run.py                 ← Run ORM model
│   │   │   │   ├── metric_snapshot.py     ← MetricSnapshot ORM model
│   │   │   │   ├── artifact.py            ← Artifact ORM model
│   │   │   │   └── user.py                ← User ORM model
│   │   │   └── repositories/
│   │   │       ├── run_repo.py            ← All DB queries for runs
│   │   │       ├── metric_repo.py         ← All DB queries for metric snapshots
│   │   │       └── artifact_repo.py       ← All DB queries for artifacts
│   │   ├── schemas/
│   │   │   ├── run.py                     ← RunCreate, RunRead, RunUpdate, RunStatus
│   │   │   ├── metric.py                  ← MetricCreate, MetricRead, MetricBatch
│   │   │   ├── artifact.py                ← ArtifactCreate, ArtifactRead
│   │   │   └── user.py                    ← UserCreate, UserRead, Token
│   │   ├── services/
│   │   │   ├── run_service.py             ← Business logic: create, update, delete runs
│   │   │   ├── stream_service.py          ← Redis XADD writer, XRANGE reader, SSE publisher
│   │   │   └── artifact_service.py        ← File save/retrieve (volume or MinIO)
│   │   └── workers/
│   │       └── persist_worker.py          ← Background task: Redis → PostgreSQL every 10 steps
│   ├── alembic/
│   │   ├── env.py                         ← Alembic env (async SQLAlchemy)
│   │   ├── script.py.mako
│   │   └── versions/                      ← Auto-generated migration files
│   ├── tests/
│   │   ├── conftest.py                    ← Pytest fixtures: test DB, test Redis, AsyncClient
│   │   ├── unit/
│   │   │   ├── test_schemas.py
│   │   │   ├── test_services.py
│   │   │   └── test_stream_service.py
│   │   └── integration/
│   │       ├── test_runs_api.py           ← POST/GET/PATCH/DELETE /runs
│   │       ├── test_metrics_api.py        ← POST metric → Redis → SSE delivery
│   │       └── test_health.py
│   ├── Dockerfile                         ← Multi-stage: builder + slim runtime
│   ├── pyproject.toml                     ← Project metadata + dev dependencies
│   └── requirements.txt                   ← Pinned production dependencies
│
├── frontend/
│   ├── src/
│   │   ├── main.tsx                       ← ReactDOM.createRoot, React Query provider
│   │   ├── App.tsx                        ← Router setup, layout wrapper
│   │   ├── pages/
│   │   │   ├── RunsListPage.tsx           ← /runs — table of all experiments
│   │   │   ├── RunDetailPage.tsx          ← /runs/:id — live chart + metadata
│   │   │   ├── ComparePage.tsx            ← /compare?ids=a,b,c — overlaid charts
│   │   │   ├── LeaderboardPage.tsx        ← /leaderboard — ranked by macro F1
│   │   │   └── NotFoundPage.tsx
│   │   ├── components/
│   │   │   ├── charts/
│   │   │   │   ├── LiveLossChart.tsx      ← Recharts LineChart + SSE hook
│   │   │   │   ├── CompareChart.tsx       ← Multi-run overlay, min-max normalized
│   │   │   │   ├── MetricCard.tsx         ← Single metric stat (F1, accuracy, etc.)
│   │   │   │   └── EpochTable.tsx         ← Scrollable table of all metric snapshots
│   │   │   ├── runs/
│   │   │   │   ├── RunsTable.tsx          ← TanStack Table, sortable/filterable
│   │   │   │   ├── RunRow.tsx             ← Single row with status badge
│   │   │   │   ├── RunStatusBadge.tsx     ← queued/running/completed/failed badge
│   │   │   │   ├── HyperparamDiff.tsx     ← Side-by-side hyperparam comparison
│   │   │   │   ├── RunCreateForm.tsx      ← Form to start a new run (optional UI)
│   │   │   │   └── TagFilter.tsx          ← Tag search + multi-select filter
│   │   │   ├── layout/
│   │   │   │   ├── Sidebar.tsx            ← Nav: Runs / Compare / Leaderboard
│   │   │   │   ├── TopBar.tsx             ← Search input + user menu
│   │   │   │   └── PageShell.tsx          ← Sidebar + TopBar + main content area
│   │   │   └── ui/                        ← shadcn/ui components (auto-generated)
│   │   │       ├── button.tsx
│   │   │       ├── badge.tsx
│   │   │       ├── card.tsx
│   │   │       ├── dialog.tsx
│   │   │       ├── input.tsx
│   │   │       ├── select.tsx
│   │   │       └── table.tsx
│   │   ├── hooks/
│   │   │   ├── useSSEMetrics.ts           ← EventSource connection + state management
│   │   │   ├── useRuns.ts                 ← TanStack Query hooks for run CRUD
│   │   │   ├── useRunDetail.ts            ← Single run query + polling for status
│   │   │   └── useCompare.ts              ← Multi-run fetch + normalization
│   │   ├── store/
│   │   │   └── useAppStore.ts             ← Zustand: selectedRunIds, filters, theme
│   │   ├── lib/
│   │   │   ├── api.ts                     ← axios instance with base URL + interceptors
│   │   │   ├── ema.ts                     ← EMA smoother: α=0.1, user-adjustable
│   │   │   ├── normalize.ts               ← Min-max normalization for compare chart
│   │   │   └── formatters.ts              ← Duration, timestamp, metric formatters
│   │   └── types/
│   │       ├── run.ts                     ← Run, RunStatus, HyperParams TypeScript types
│   │       └── metric.ts                  ← MetricPoint, MetricHistory types
│   ├── index.html
│   ├── vite.config.ts                     ← Proxy /api → backend:8000
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   ├── package.json
│   └── Dockerfile                         ← Multi-stage: node build → nginx serve
│
├── sdk/
│   ├── ml_tracker/
│   │   ├── __init__.py                    ← exports: Run, log_metric, finish
│   │   ├── client.py                      ← HTTP client (httpx sync + async)
│   │   ├── run.py                         ← Run class: create, log_metric, log_hyperparams, finish
│   │   └── exceptions.py                  ← TrackerConnectionError, RunNotFoundError
│   ├── tests/
│   │   ├── test_client.py
│   │   └── test_run.py
│   ├── pyproject.toml                     ← pip-installable: pip install ml-tracker
│   └── README.md                          ← SDK usage guide
│
├── k8s/
│   ├── base/
│   │   ├── postgres-statefulset.yaml      ← StatefulSet + PVC + Service
│   │   ├── redis-deployment.yaml          ← Deployment + Service
│   │   ├── api-deployment.yaml            ← Deployment (3 replicas) + Service + HPA
│   │   ├── frontend-deployment.yaml       ← Deployment + Service
│   │   ├── ingress.yaml                   ← NGINX: / → frontend, /api → backend
│   │   ├── secrets.yaml                   ← DB_URL, REDIS_URL, JWT_SECRET (base64)
│   │   └── configmap.yaml                 ← ENVIRONMENT=production, etc.
│   └── overlays/
│       ├── dev/kustomization.yaml         ← minikube patches (lower resources)
│       └── prod/kustomization.yaml        ← NRP.ai patches (HPA, PVC size)
│
├── scripts/
│   ├── seed_banking77.py                  ← Imports Banking77 SVM+MLP results as runs
│   ├── seed_synthetic.py                  ← Generates 50 synthetic runs for UI testing
│   ├── load_test.py                       ← 100 concurrent metric writers (httpx async)
│   └── reset_db.sh                        ← Drop + recreate schema (dev only)
│
├── .github/
│   └── workflows/
│       ├── ci.yml                         ← On PR: pytest + eslint + docker build
│       └── deploy.yml                     ← On merge to main: push GHCR + kubectl apply
│
├── docker-compose.yml                     ← postgres + redis + minio + api + frontend
├── docker-compose.test.yml                ← postgres-test + redis-test (isolated)
├── .env.example                           ← Template for .env (committed)
├── .env                                   ← Real secrets (gitignored)
├── .gitignore
└── README.md
```

---

## DATABASE SCHEMA (Full SQL)

```sql
-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ── USERS ────────────────────────────────────────────────────────────────────
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ── EXPERIMENTS (RUNS) ───────────────────────────────────────────────────────
CREATE TYPE run_status AS ENUM ('queued', 'running', 'completed', 'failed');

CREATE TABLE runs (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name             VARCHAR(255) NOT NULL,
    model_type       VARCHAR(100),
    dataset          VARCHAR(255),
    status           run_status DEFAULT 'queued',
    hyperparams      JSONB DEFAULT '{}',
    final_metrics    JSONB DEFAULT '{}',
    tags             TEXT[] DEFAULT '{}',
    notes            TEXT,
    user_id          UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    completed_at     TIMESTAMPTZ,
    duration_seconds DOUBLE PRECISION
);
-- Indexes for common queries
CREATE INDEX idx_runs_status     ON runs(status);
CREATE INDEX idx_runs_created_at ON runs(created_at DESC);
CREATE INDEX idx_runs_tags       ON runs USING GIN(tags);
CREATE INDEX idx_runs_hyperparams ON runs USING GIN(hyperparams);

-- ── METRIC SNAPSHOTS ─────────────────────────────────────────────────────────
CREATE TABLE metric_snapshots (
    id            BIGSERIAL PRIMARY KEY,
    run_id        UUID NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    step          INTEGER NOT NULL,         -- epoch or batch number
    metrics       JSONB NOT NULL,           -- {"loss":0.54,"val_loss":0.61,"acc":0.85}
    recorded_at   TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(run_id, step)
);
CREATE INDEX idx_snapshots_run_id_step ON metric_snapshots(run_id, step);

-- ── ARTIFACTS ────────────────────────────────────────────────────────────────
CREATE TYPE artifact_type AS ENUM (
    'confusion_matrix', 'roc_curve', 'pr_curve',
    'model_weights', 'custom_plot', 'other'
);

CREATE TABLE artifacts (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id        UUID NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    artifact_type artifact_type NOT NULL,
    filename      VARCHAR(255) NOT NULL,
    file_path     TEXT NOT NULL,            -- path in MinIO or local volume
    size_bytes    INTEGER,
    created_at    TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_artifacts_run_id ON artifacts(run_id);
```

---

## API ENDPOINTS (Full Specification)

### Base URL: `/api/v1`

#### Runs

| Method | Path | Request Body | Response | Description |
|---|---|---|---|---|
| `POST` | `/runs` | `RunCreate` | `RunRead` 201 | Create a new run |
| `GET` | `/runs` | query: `status`, `tags`, `search`, `limit`, `offset` | `List[RunRead]` | List runs, filterable |
| `GET` | `/runs/{run_id}` | — | `RunRead` | Get single run |
| `PATCH` | `/runs/{run_id}` | `RunUpdate` | `RunRead` | Update status, notes, tags |
| `DELETE` | `/runs/{run_id}` | — | 204 | Delete run + cascade |

**RunCreate schema:**
```json
{
  "name": "banking77-mlp-v3",
  "model_type": "DeepMLP",
  "dataset": "banking77",
  "hyperparams": {"lr": 0.001, "epochs": 50, "dropout": 0.3, "batch_size": 64},
  "tags": ["mlp", "tfidf", "banking77"]
}
```

**RunRead schema:**
```json
{
  "id": "3f2a8b1c-...",
  "name": "banking77-mlp-v3",
  "model_type": "DeepMLP",
  "dataset": "banking77",
  "status": "running",
  "hyperparams": {"lr": 0.001, "epochs": 50},
  "final_metrics": {},
  "tags": ["mlp", "tfidf"],
  "created_at": "2026-06-03T18:00:00Z",
  "completed_at": null,
  "duration_seconds": null
}
```

---

#### Metrics

| Method | Path | Request Body | Response | Description |
|---|---|---|---|---|
| `POST` | `/runs/{run_id}/metrics` | `MetricCreate` | 201 | Log one epoch's metrics → Redis XADD + PostgreSQL persist |
| `POST` | `/runs/{run_id}/metrics/batch` | `List[MetricCreate]` | 201 | Batch log (end-of-training replay) |
| `GET` | `/runs/{run_id}/metrics` | query: `from_step`, `to_step` | `List[MetricRead]` | Full metric history from PostgreSQL |
| `GET` | `/runs/{run_id}/stream` | — | SSE stream | Live metric SSE (EventSource) |

**MetricCreate schema:**
```json
{
  "step": 9,
  "metrics": {
    "loss": 0.5332,
    "val_loss": 0.5449,
    "accuracy": 0.8918,
    "val_accuracy": 0.8553
  }
}
```

**SSE stream message format:**
```
event: metric
data: {"step":9,"loss":0.5332,"val_loss":0.5449,"accuracy":0.8918,"val_accuracy":0.8553,"ts":1717430400.123}

event: status_change
data: {"run_id":"3f2a8b1c-...","status":"completed","final_metrics":{"macro_f1":0.8599}}

event: heartbeat
data: {"ts":1717430405.000}
```

---

#### Artifacts

| Method | Path | Request Body | Response | Description |
|---|---|---|---|---|
| `POST` | `/runs/{run_id}/artifacts` | multipart/form-data | `ArtifactRead` 201 | Upload file |
| `GET` | `/runs/{run_id}/artifacts` | — | `List[ArtifactRead]` | List artifacts for run |
| `GET` | `/artifacts/{artifact_id}/download` | — | file bytes | Download artifact |

---

#### Health

| Method | Path | Response |
|---|---|---|
| `GET` | `/health` | `{"status":"ok","db":"connected","redis":"connected","version":"0.1.0"}` |

---

## REDIS STREAM DESIGN

### Stream keys
```
experiment:{run_id}:metrics      ← per-run metric stream
```

### XADD message fields
```python
await redis.xadd(
    f"experiment:{run_id}:metrics",
    {
        "step":          str(step),
        "loss":          str(metrics.get("loss", "")),
        "val_loss":      str(metrics.get("val_loss", "")),
        "accuracy":      str(metrics.get("accuracy", "")),
        "val_accuracy":  str(metrics.get("val_accuracy", "")),
        "ts":            str(time.time()),
    },
    maxlen=1000,     # cap stream to last 1000 entries
)
```

### SSE consumer (stream_service.py)
```python
async def sse_metric_stream(run_id: str, redis):
    """
    Yield SSE-formatted lines from Redis stream.
    Starts from $ (only future messages) unless run is already completed
    (in which case starts from 0 to replay history).
    """
    last_id = "0" if run_is_completed else "$"
    while True:
        messages = await redis.xread(
            {f"experiment:{run_id}:metrics": last_id},
            block=2000,   # block 2s, then yield heartbeat
            count=50,
        )
        if messages:
            for _, entries in messages:
                for entry_id, fields in entries:
                    last_id = entry_id
                    yield f"event: metric\ndata: {json.dumps(fields)}\n\n"
        else:
            yield f"event: heartbeat\ndata: {json.dumps({'ts': time.time()})}\n\n"
        if await run_is_done(run_id):
            break
```

### Background persist worker (persist_worker.py)
```python
# Runs as FastAPI lifespan background task
# Every 10 steps: read new entries from Redis → INSERT INTO metric_snapshots
async def persist_loop(redis, db_session_factory):
    while True:
        await asyncio.sleep(5)   # check every 5 seconds
        for run_id in await get_active_run_ids():
            entries = await redis.xrange(
                f"experiment:{run_id}:metrics",
                min=last_persisted_id[run_id],
            )
            if entries:
                snapshots = [parse_entry(e) for e in entries]
                await metric_repo.bulk_insert(db, snapshots)
                last_persisted_id[run_id] = entries[-1][0]
```

---

## PYTHON SDK DESIGN

### Installation
```bash
pip install ml-tracker   # from PyPI (Phase 5) or local: pip install -e ./sdk
```

### Usage (in any training script)
```python
from ml_tracker import Run

# 1. Create a run
run = Run.create(
    tracker_url="http://localhost:8000",
    name="banking77-mlp-v3",
    model_type="DeepMLP",
    dataset="banking77",
    hyperparams={"lr": 0.001, "epochs": 50, "dropout": 0.3},
    tags=["mlp", "tfidf"],
)

# 2. Log hyperparams (can also add mid-run)
run.log_hyperparams({"batch_size": 64})

# 3. Training loop
for epoch in range(50):
    # ... your training code ...
    run.log_metric(
        step=epoch,
        loss=train_loss,
        val_loss=val_loss,
        accuracy=train_acc,
        val_accuracy=val_acc,
    )

# 4. Finish (marks run complete, logs final metrics)
run.finish(final_metrics={"macro_f1": 0.8599, "roc_auc": 0.9960})
```

### SDK internals (client.py)
```python
import httpx

class TrackerClient:
    def __init__(self, base_url: str, timeout: float = 5.0):
        self._client = httpx.Client(base_url=base_url, timeout=timeout)

    def create_run(self, payload: dict) -> dict:
        r = self._client.post("/api/v1/runs", json=payload)
        r.raise_for_status()
        return r.json()

    def log_metric(self, run_id: str, step: int, metrics: dict):
        r = self._client.post(
            f"/api/v1/runs/{run_id}/metrics",
            json={"step": step, "metrics": metrics},
        )
        r.raise_for_status()

    def finish_run(self, run_id: str, final_metrics: dict):
        self._client.patch(
            f"/api/v1/runs/{run_id}",
            json={"status": "completed", "final_metrics": final_metrics},
        )
```

---

## REACT COMPONENT DATA FLOW

```
App.tsx
└── PageShell.tsx (Sidebar + TopBar)
    ├── RunsListPage.tsx
    │   └── RunsTable.tsx
    │       ├── useRuns() → GET /api/v1/runs → TanStack Query cache
    │       ├── RunRow.tsx × N
    │       │   └── RunStatusBadge.tsx
    │       └── TagFilter.tsx → updates Zustand filter state
    │
    ├── RunDetailPage.tsx  (/runs/:id)
    │   ├── useRunDetail(id) → GET /api/v1/runs/:id (polls every 3s if running)
    │   ├── MetricCard.tsx × 4  (final F1, ROC-AUC, best val_loss, duration)
    │   ├── LiveLossChart.tsx
    │   │   ├── useSSEMetrics(id) → EventSource /api/v1/runs/:id/stream
    │   │   │   └── useState([]) ← appends each SSE metric message
    │   │   └── Recharts <LineChart> re-renders on state change
    │   ├── EpochTable.tsx  ← GET /api/v1/runs/:id/metrics (on load, not SSE)
    │   └── HyperparamDiff.tsx  ← shows run's hyperparams as key-value
    │
    ├── ComparePage.tsx  (/compare?ids=a,b,c)
    │   ├── useCompare([id1,id2,...]) → parallel GET /api/v1/runs/:id/metrics
    │   ├── normalize(series) → lib/normalize.ts min-max per metric
    │   └── CompareChart.tsx
    │       └── Recharts <LineChart> with multiple <Line> series (one per run)
    │
    └── LeaderboardPage.tsx  (/leaderboard)
        └── RunsTable filtered by final_metrics.macro_f1 DESC
```

### useSSEMetrics hook (hooks/useSSEMetrics.ts)
```typescript
export function useSSEMetrics(runId: string) {
  const [points, setPoints] = useState<MetricPoint[]>([]);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const es = new EventSource(`/api/v1/runs/${runId}/stream`);
    setConnected(true);

    es.addEventListener("metric", (e) => {
      const pt = JSON.parse(e.data) as MetricPoint;
      setPoints((prev) => [...prev, pt]);
    });

    es.addEventListener("status_change", (e) => {
      const { status } = JSON.parse(e.data);
      if (status === "completed" || status === "failed") {
        es.close();
        setConnected(false);
      }
    });

    es.onerror = () => {
      es.close();
      setConnected(false);
    };

    return () => { es.close(); setConnected(false); };
  }, [runId]);

  return { points, connected };
}
```

---

## DOCKER COMPOSE (Full Definition)

```yaml
# docker-compose.yml
services:

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: ml_tracker
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ml_tracker
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ml_tracker"]
      interval: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      retries: 5

  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: ${MINIO_SECRET_KEY}
    volumes:
      - minio_data:/data
    ports:
      - "9000:9000"
      - "9001:9001"

  api:
    build: ./backend
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    volumes:
      - ./backend:/app
    env_file: .env
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy

  frontend:
    build: ./frontend
    command: npm run dev -- --host 0.0.0.0
    volumes:
      - ./frontend:/app
      - /app/node_modules
    ports:
      - "5173:5173"
    depends_on:
      - api

volumes:
  postgres_data:
  minio_data:
```

---

## KUBERNETES MANIFESTS (K8s Key Files)

### api-deployment.yaml
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
spec:
  replicas: 3
  selector:
    matchLabels: {app: api}
  template:
    metadata:
      labels: {app: api}
    spec:
      containers:
      - name: api
        image: ghcr.io/tabrez05/ml-experiment-tracker-api:latest
        ports: [{containerPort: 8000}]
        envFrom:
          - secretRef: {name: app-secrets}
          - configMapRef: {name: app-config}
        resources:
          requests: {cpu: 500m, memory: 512Mi}
          limits:   {cpu: 1,    memory: 1Gi}
        livenessProbe:
          httpGet: {path: /api/v1/health, port: 8000}
          initialDelaySeconds: 10
          periodSeconds: 10
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api
  minReplicas: 2
  maxReplicas: 8
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 60
```

---

## GITHUB ACTIONS CI/CD

### .github/workflows/ci.yml (on every PR)
```yaml
name: CI
on: [pull_request]
jobs:
  backend-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env: {POSTGRES_USER: test, POSTGRES_PASSWORD: test, POSTGRES_DB: test}
        ports: ["5432:5432"]
        options: --health-cmd pg_isready
      redis:
        image: redis:7
        ports: ["6379:6379"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: "3.11"}
      - run: pip install -r backend/requirements.txt
      - run: pytest backend/tests/ -v --tb=short
        env:
          DATABASE_URL: postgresql+asyncpg://test:test@localhost/test
          REDIS_URL: redis://localhost:6379/0
          SECRET_KEY: ci-test-secret

  frontend-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: {node-version: "20"}
      - run: cd frontend && npm ci && npm run lint && npm run test
```

### .github/workflows/deploy.yml (on merge to main)
```yaml
name: Deploy
on:
  push:
    branches: [main]
jobs:
  build-push-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Login to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: tabrez05
          password: ${{ secrets.GHCR_TOKEN }}
      - name: Build + push API
        uses: docker/build-push-action@v5
        with:
          context: ./backend
          push: true
          tags: ghcr.io/tabrez05/ml-experiment-tracker-api:latest
      - name: Build + push Frontend
        uses: docker/build-push-action@v5
        with:
          context: ./frontend
          push: true
          tags: ghcr.io/tabrez05/ml-experiment-tracker-frontend:latest
      - name: Deploy to Kubernetes
        uses: tale/kubectl-action@v1
        with:
          base64-kube-config: ${{ secrets.KUBE_CONFIG }}
      - run: kubectl rollout restart deployment/api deployment/frontend -n ml-tracker
```

---

## PHASE EXECUTION ORDER

### Phase 1 — Core API + Database (Start here)

**Files to create in order:**

```
1.  docker-compose.yml              ← postgres + redis + minio (no app yet)
2.  .env.example + .env             ← all env vars
3.  backend/requirements.txt        ← pinned deps
4.  backend/app/core/config.py      ← Settings with pydantic-settings
5.  backend/app/db/session.py       ← AsyncEngine + Base + get_db()
6.  backend/app/db/models/run.py    ← Run ORM model
7.  backend/app/db/models/metric_snapshot.py
8.  backend/alembic/env.py          ← async alembic setup
9.  alembic revision --autogenerate → first migration
10. backend/app/schemas/run.py      ← RunCreate, RunRead, RunUpdate
11. backend/app/db/repositories/run_repo.py
12. backend/app/services/run_service.py
13. backend/app/api/v1/endpoints/runs.py
14. backend/app/api/v1/router.py
15. backend/app/api/v1/endpoints/health.py
16. backend/app/main.py             ← app factory, include router
17. backend/Dockerfile
18. docker-compose.yml              ← add api service
19. backend/tests/conftest.py
20. backend/tests/integration/test_runs_api.py
21. scripts/seed_banking77.py       ← import SVM + MLP results as first 2 runs
```

**Milestone check:**
```bash
docker compose up -d postgres redis
cd backend && alembic upgrade head
uvicorn app.main:app --reload
curl http://localhost:8000/api/v1/health
# → {"status":"ok","db":"connected","redis":"connected"}
curl -X POST http://localhost:8000/api/v1/runs \
  -H "Content-Type: application/json" \
  -d '{"name":"banking77-svm","model_type":"LinearSVC","dataset":"banking77"}'
# → {"id":"...","status":"queued",...}
```

---

### Phase 2 — Redis Streams + SSE
Files: `stream_service.py`, `metrics.py` endpoint, `persist_worker.py`, SSE route

**Milestone check:**
```bash
# Terminal 1: POST a metric every second (simulate training)
for i in $(seq 1 20); do
  curl -s -X POST http://localhost:8000/api/v1/runs/{RUN_ID}/metrics \
    -H "Content-Type: application/json" \
    -d "{\"step\":$i,\"metrics\":{\"loss\":$(python3 -c \"import random;print(round(1/($i+1)+random.uniform(-0.05,0.05),4))\")}}"
  sleep 1
done

# Terminal 2: Listen to SSE stream
curl -N http://localhost:8000/api/v1/runs/{RUN_ID}/stream
# → event: metric, data: {"step":1,"loss":0.91,...}
# → event: metric, data: {"step":2,"loss":0.74,...}
```

---

### Phase 3 — React Frontend
```bash
cd frontend
npm create vite@latest . -- --template react-ts
npm install recharts @tanstack/react-query @tanstack/react-table zustand axios react-router-dom
npx tailwindcss init -p
npx shadcn-ui@latest init
```

**Milestone check:** Open browser at `http://localhost:5173`:
- `/runs` shows Banking77 SVM and MLP as two rows in a table
- `/runs/{mlp_id}` shows a live loss curve chart
- `/compare?ids=svm_id,mlp_id` overlays both curves

---

### Phase 4 — Docker + Kubernetes
```bash
# Full stack in Docker
docker compose up --build
# Verify all 5 services healthy: postgres, redis, minio, api, frontend

# Local Kubernetes
minikube start --cpus 4 --memory 8192
kubectl apply -f k8s/base/
kubectl get pods -n ml-tracker -w
# All pods Running within 90 seconds
```

---

### Phase 5 — GitHub Actions CI/CD
1. Create GitHub repo `tabrez05/ml-experiment-tracker`
2. Add repository secrets: `GHCR_TOKEN`, `KUBE_CONFIG`, `POSTGRES_PASSWORD`, `SECRET_KEY`
3. Push to a PR branch → verify CI runs green
4. Merge to main → verify images appear in GHCR → verify k8s pods restart with new image

---

### Phase 6 — Polish
- SDK published: `pip install ml-tracker` (TestPyPI first)
- `scripts/seed_synthetic.py` — 50 runs for UI stress test
- `scripts/load_test.py` — 100 concurrent writers, measure p95 latency
- README with architecture diagram, screenshots, and demo GIF

---

## DEPENDENCY LIST (requirements.txt — backend)

```
fastapi==0.111.0
uvicorn[standard]==0.29.0
sqlalchemy[asyncio]==2.0.30
alembic==1.13.1
asyncpg==0.29.0
redis[asyncio]==5.0.4
pydantic==2.7.1
pydantic-settings==2.2.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.9
httpx==0.27.0
pytest==8.2.0
pytest-asyncio==0.23.6
pytest-cov==5.0.0
```

## DEPENDENCY LIST (package.json — frontend key deps)

```json
"dependencies": {
  "react": "^18.3.0",
  "react-dom": "^18.3.0",
  "react-router-dom": "^6.23.0",
  "recharts": "^2.12.0",
  "@tanstack/react-query": "^5.37.0",
  "@tanstack/react-table": "^8.17.0",
  "zustand": "^4.5.0",
  "axios": "^1.7.0",
  "tailwindcss": "^3.4.0",
  "clsx": "^2.1.0"
},
"devDependencies": {
  "vite": "^5.2.0",
  "vitest": "^1.6.0",
  "@types/react": "^18.3.0",
  "typescript": "^5.4.0",
  "eslint": "^9.0.0"
}
```

---

## FIRST COMMAND TO RUN RIGHT NOW

```bash
cd "/Users/tbz/581-ML/Project-Final/ML-Project/ML-expirement tracker/ml-experiment-tracker"
docker compose up -d postgres redis minio
docker compose ps
# All three should show "healthy" — this is the green light to start Phase 1
```

---

*Low-level implementation plan complete. Phase 1 begins immediately after docker compose health check passes.*
