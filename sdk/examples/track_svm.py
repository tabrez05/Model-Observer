"""
Example: track an sklearn SVM experiment using the SDK.

Run from the ml-experiment-tracker root:
    python sdk/examples/track_svm.py
"""
import sys
sys.path.insert(0, "sdk")  # allow running without installing

import random
import ml_tracker
from ml_tracker.callbacks import log_cv_results

random.seed(42)

# ── Simulated training (replace with your real code) ──────────────────────────

PARAM_GRID = [0.1, 1.0, 10.0]   # C values

cv_results = {
    "mean_test_score": [0.8521, 0.8799, 0.8741],
    "std_test_score":  [0.0031, 0.0028, 0.0034],
    "mean_fit_time":   [2.1, 3.7, 4.2],
    "params":          [{"C": c} for c in PARAM_GRID],
}

best_idx = cv_results["mean_test_score"].index(max(cv_results["mean_test_score"]))
best_C   = PARAM_GRID[best_idx]

print(f"Best C={best_C}  CV F1={cv_results['mean_test_score'][best_idx]:.4f}")

# ── Track with SDK ─────────────────────────────────────────────────────────────

with ml_tracker.init(
    name=f"svm-sdk-demo-C{best_C}",
    model_type="LinearSVC",
    dataset="banking77",
    hyperparams={"C": best_C, "ngram_range": "(1,2)", "max_features": 10000, "cv_folds": 5},
    tags=["svm", "sdk-demo", "banking77"],
    notes="Tracked via ml-tracker-sdk example.",
) as run:

    # Log each CV fold result as a step
    for i, (score, C) in enumerate(zip(cv_results["mean_test_score"], PARAM_GRID)):
        run.log({"cv_f1": score, "C": C}, step=i)

    # Log full CV results summary
    log_cv_results(run, cv_results, step=len(PARAM_GRID))

    # Final test-set evaluation (simulated)
    run.finish(final_metrics={
        "macro_f1": 0.8862,
        "micro_f1": 0.8859,
        "accuracy": 0.8859,
        "pr_auc":   0.9228,
        "roc_auc":  0.9951,
        "train_time_s": 3.67,
    })

print(f"\nRun tracked!  View at: http://localhost:5200/runs/{run.id}")
