"""
Optional framework callbacks.

Keras:
    from ml_tracker.callbacks import KerasCallback
    model.fit(..., callbacks=[KerasCallback(run)])

Sklearn (manual wrapper):
    from ml_tracker.callbacks import log_cv_results
    log_cv_results(run, cv_results, step=0)
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .run import Run


# ── Keras ─────────────────────────────────────────────────────────────────────

def _make_keras_callback(run: "Run"):  # type: ignore[return]
    try:
        from tensorflow.keras.callbacks import Callback  # type: ignore
    except ImportError:
        raise ImportError("TensorFlow is required for KerasCallback. pip install tensorflow")

    class KerasCallback(Callback):
        """Logs epoch metrics to the ML Tracker after every epoch."""

        def on_epoch_end(self, epoch: int, logs: dict | None = None) -> None:
            if logs:
                run.log(metrics={k: float(v) for k, v in logs.items()}, step=epoch + 1)

        def on_train_end(self, logs: dict | None = None) -> None:
            final = {k: float(v) for k, v in (logs or {}).items()}
            run.finish(final_metrics=final if final else None)

    return KerasCallback()


KerasCallback = _make_keras_callback


# ── Sklearn ───────────────────────────────────────────────────────────────────

def log_cv_results(run: "Run", cv_results: dict[str, Any], step: int = 0) -> None:
    """
    Log sklearn GridSearchCV / cross_validate results as a single metric snapshot.

    Example:
        gs = GridSearchCV(clf, param_grid, scoring="f1_macro", cv=5)
        gs.fit(X_train, y_train)
        log_cv_results(run, gs.cv_results_, step=0)
    """
    metrics: dict[str, float] = {}
    for key in ("mean_test_score", "std_test_score", "mean_fit_time"):
        if key in cv_results:
            val = cv_results[key]
            if hasattr(val, "__iter__"):
                metrics[key] = float(max(val))
            else:
                metrics[key] = float(val)
    run.log(metrics=metrics, step=step)
