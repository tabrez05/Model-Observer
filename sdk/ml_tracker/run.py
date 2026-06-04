"""Run context manager — the primary user-facing API."""
from __future__ import annotations

import time
import traceback
from typing import Any

from .client import TrackerClient


class Run:
    """
    Represents a single tracked experiment run.

    Usage:
        with ml_tracker.init(name="my-svm", model_type="SVM", dataset="Banking77") as run:
            run.log(step=0, loss=0.5, accuracy=0.82)
            run.finish(final_metrics={"f1_macro": 0.88})
    """

    def __init__(self, client: TrackerClient, run_id: str, name: str):
        self._client = client
        self.id = run_id
        self.name = name
        self._start = time.time()
        self._step = 0

    # ── Logging ───────────────────────────────────────────────────────────────

    def log(self, metrics: dict[str, float], step: int | None = None) -> None:
        """Log a metric snapshot.  If step is omitted, auto-increments."""
        if step is None:
            self._step += 1
            step = self._step
        else:
            self._step = step
        self._client.log_metric(self.id, step, metrics)

    def finish(
        self,
        final_metrics: dict[str, float] | None = None,
        status: str = "completed",
    ) -> None:
        """Mark the run as completed and record final metrics."""
        duration = round(time.time() - self._start, 2)
        self._client.update_run(
            self.id,
            status=status,
            final_metrics=final_metrics or {},
            duration_seconds=duration,
        )

    # ── Context manager ───────────────────────────────────────────────────────

    def __enter__(self) -> "Run":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if exc_type is not None:
            # Training crashed — mark failed
            self._client.update_run(
                self.id,
                status="failed",
                notes=f"Exception: {exc_type.__name__}: {exc_val}\n"
                      + "".join(traceback.format_tb(exc_tb)),
            )
        elif self._client.get_run(self.id)["status"] == "running":
            # Exited without calling finish() — auto-complete
            self.finish()

    def __repr__(self) -> str:
        return f"<Run id={self.id!r} name={self.name!r}>"
