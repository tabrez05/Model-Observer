# ML Experiment Tracker

A production-grade MLOps platform to log, compare, and visualize ML training runs in real time.

**Stack**: FastAPI · PostgreSQL · Redis Streams · React · Docker · Kubernetes · GitHub Actions

---

## Quick Start (Docker — recommended)

```bash
cp .env.example .env          # edit secrets if needed
docker compose up -d --build  # starts all 5 services + runs migrations
```

| Service   | URL                           |
|-----------|-------------------------------|
| Dashboard | http://localhost:5173         |
| API docs  | http://localhost:8000/docs    |
| MinIO     | http://localhost:9001         |

Seed with Banking77 demo data:
```bash
docker compose exec api python /scripts/seed_banking77.py
```

---

## Local Development (without Docker)

```bash
# Prerequisites: PostgreSQL 16, Redis 7 running locally

cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload        # http://localhost:8000

# In a second terminal:
cd frontend
npm install
npm run dev                          # http://localhost:5173
```

---

## Python SDK

Track any training script in 3 lines:

```bash
pip install -e sdk/
```

```python
import ml_tracker

with ml_tracker.init(
    name="my-svm",
    model_type="LinearSVC",
    dataset="banking77",
    hyperparams={"C": 1.0},
    tags=["baseline"],
) as run:
    for epoch, metrics in training_loop():
        run.log(metrics, step=epoch)
    run.finish(final_metrics={"f1_macro": 0.886})
```

**Keras callback:**
```python
from ml_tracker.callbacks import KerasCallback
model.fit(X, y, callbacks=[KerasCallback(run)])
```

---

## Project Structure

```
ml-experiment-tracker/
├── backend/                  # FastAPI + SQLAlchemy + Alembic
│   ├── app/
│   │   ├── api/v1/endpoints/ # runs, metrics, health
│   │   ├── db/               # models, repositories, session
│   │   ├── schemas/          # Pydantic schemas
│   │   └── services/         # Redis stream service
│   ├── alembic/              # migrations
│   └── tests/                # pytest integration tests
├── frontend/                 # React 18 + Vite + Tailwind + Recharts
│   └── src/
│       ├── pages/            # RunsList, RunDetail, Compare, NewRun
│       ├── components/       # LiveChart, CompareChart, StatusBadge
│       └── hooks/            # useSSE (Server-Sent Events)
├── sdk/                      # pip-installable Python SDK
│   └── ml_tracker/
│       ├── __init__.py       # ml_tracker.init()
│       ├── client.py         # HTTP client
│       ├── run.py            # Run context manager
│       └── callbacks.py      # Keras + sklearn callbacks
├── k8s/                      # Kubernetes manifests (Kustomize)
│   ├── base/
│   └── overlays/{dev,prod}/
├── scripts/                  # seed_banking77.py, demo_live_run.py
├── docker-compose.yml        # dev stack
├── docker-compose.prod.yml   # production overrides
└── .github/workflows/
    ├── ci.yml                # test + build on every PR
    └── cd.yml                # push images + deploy on tag
```

---

## CI/CD

| Trigger | Action |
|---|---|
| Push to any branch / PR | Run backend tests + frontend build |
| Push to `main` | Build & push Docker images to GHCR |
| Push tag `v*.*.*` | Deploy to GKE via kubectl + Kustomize |

To deploy a new version:
```bash
git tag v1.0.0 && git push origin v1.0.0
```

---

## Kubernetes (minikube local)

```bash
minikube start
kubectl apply -k k8s/overlays/dev
kubectl port-forward svc/frontend 8080:80 -n ml-tracker
```

For GKE production, set these GitHub secrets:
`GCP_SA_KEY`, `GKE_CLUSTER`, `GKE_ZONE`
