"""Low-level HTTP client — thin wrapper around httpx."""
from __future__ import annotations

from typing import Any

import httpx


class TrackerClient:
    def __init__(self, base_url: str = "http://localhost:8000", timeout: float = 10.0):
        self._http = httpx.Client(base_url=base_url.rstrip("/"), timeout=timeout)

    # ── Runs ──────────────────────────────────────────────────────────────────

    def create_run(self, **kwargs: Any) -> dict:
        return self._http.post("/api/v1/runs", json=kwargs).raise_for_status().json()

    def update_run(self, run_id: str, **kwargs: Any) -> dict:
        return self._http.patch(f"/api/v1/runs/{run_id}", json=kwargs).raise_for_status().json()

    def get_run(self, run_id: str) -> dict:
        return self._http.get(f"/api/v1/runs/{run_id}").raise_for_status().json()

    # ── Metrics ───────────────────────────────────────────────────────────────

    def log_metric(self, run_id: str, step: int, metrics: dict[str, float]) -> None:
        self._http.post(
            f"/api/v1/runs/{run_id}/metrics",
            json={"step": step, "metrics": metrics},
        ).raise_for_status()

    def close(self) -> None:
        self._http.close()
