# ── Stage 1: development (hot-reload) ─────────────────────────────────────────
FROM python:3.11-slim AS development
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ── Stage 2: production (optimized) ───────────────────────────────────────────
FROM python:3.11-slim AS production
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn
COPY . .
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", "--timeout", "120"]
