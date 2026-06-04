"""
ml-tracker-sdk  — log ML experiments in 3 lines.

Quick start:
    import ml_tracker

    with ml_tracker.init(
        name="my-svm-run",
        model_type="LinearSVC",
        dataset="banking77",
        hyperparams={"C": 1.0},
        tags=["baseline"],
        api_url="http://localhost:8000",   # default
    ) as run:
        for epoch, metrics in training_loop():
            run.log(metrics, step=epoch)

        run.finish(final_metrics={"f1_macro": 0.886, "accuracy": 0.886})
"""
from __future__ import annotations

from typing import Any

from .client import TrackerClient
from .run import Run

__version__ = "0.1.0"
__all__ = ["init", "Run", "TrackerClient", "__version__"]

# Module-level default client (overridable via init())
_default_url: str = "http://localhost:8000"


def init(
    name: str,
    model_type: str = "",
    dataset: str = "",
    hyperparams: dict[str, Any] | None = None,
    tags: list[str] | None = None,
    notes: str | None = None,
    api_url: str | None = None,
) -> Run:
    """
    Create and return a new tracked Run.

    Designed to be used as a context manager::

        with ml_tracker.init(name="run-1", model_type="SVM", dataset="banking77") as run:
            run.log({"loss": 0.5}, step=1)
            run.finish({"f1_macro": 0.88})

    Can also be used without ``with``::

        run = ml_tracker.init(name="run-1")
        run.log({"loss": 0.5})
        run.finish()
    """
    client = TrackerClient(base_url=api_url or _default_url)
    data = client.create_run(
        name=name,
        model_type=model_type,
        dataset=dataset,
        hyperparams=hyperparams or {},
        tags=tags or [],
        notes=notes,
        status="running",
    )
    return Run(client=client, run_id=data["id"], name=name)
