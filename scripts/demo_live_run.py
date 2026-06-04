"""
Live demo script — creates a new run and streams metrics in real-time.

Usage:
    cd ml-experiment-tracker
    source backend/venv/bin/activate
    python scripts/demo_live_run.py

Watch it live at the URL printed below.
"""
import math
import random
import time

import httpx

API = "http://localhost:8000/api/v1"

random.seed(99)

def simulate_epoch(epoch: int):
    """Simulate realistic MLP loss/accuracy curves with noise."""
    progress = epoch / 30
    loss = 3.5 * math.exp(-3.5 * progress) + 0.18 + random.gauss(0, 0.02)
    val_loss = 3.5 * math.exp(-3.0 * progress) + 0.26 + random.gauss(0, 0.03)
    accuracy = (1 - math.exp(-4.0 * progress)) * 91.0 + random.gauss(0, 0.5)
    val_accuracy = (1 - math.exp(-3.5 * progress)) * 87.0 + random.gauss(0, 0.7)
    macro_f1 = val_accuracy / 100 * 0.98
    return {
        "loss":         round(max(loss, 0.15), 4),
        "val_loss":     round(max(val_loss, 0.22), 4),
        "accuracy":     round(min(max(accuracy, 0), 100), 2),
        "val_accuracy": round(min(max(val_accuracy, 0), 100), 2),
        "macro_f1":     round(min(max(macro_f1, 0), 1), 4),
    }


def main():
    client = httpx.Client(base_url=API, timeout=10.0)

    print("Creating live demo run...")
    run = client.post("/runs", json={
        "name":        "live-demo-transformer",
        "model_type":  "Transformer",
        "dataset":     "banking77",
        "status":      "running",
        "hyperparams": {
            "lr": 3e-4,
            "epochs": 30,
            "batch_size": 128,
            "dropout": 0.1,
            "hidden_dim": 512,
            "num_heads": 8,
            "optimizer": "AdamW",
        },
        "tags": ["transformer", "live-demo", "banking77"],
        "notes": "Live streaming demo — watch the chart update in real time.",
    }).raise_for_status().json()

    run_id = run["id"]
    print(f"\n  ➜  Open this URL NOW to watch live:")
    print(f"     http://localhost:5200/runs/{run_id}")
    print(f"\n  Training 30 epochs (1 epoch/sec)...\n")

    best_val_loss = float("inf")
    best_epoch = 1

    for epoch in range(1, 31):
        metrics = simulate_epoch(epoch)
        client.post(f"/runs/{run_id}/metrics", json={"step": epoch, "metrics": metrics}).raise_for_status()

        bar = "█" * epoch + "░" * (30 - epoch)
        print(f"  Epoch {epoch:2d}/30  [{bar}]  loss={metrics['loss']:.4f}  val_acc={metrics['val_accuracy']:.1f}%  f1={metrics['macro_f1']:.4f}")

        if metrics["val_loss"] < best_val_loss:
            best_val_loss = metrics["val_loss"]
            best_epoch = epoch

        time.sleep(1.0)

    # Mark completed
    final = simulate_epoch(30)
    client.patch(f"/runs/{run_id}", json={
        "status": "completed",
        "final_metrics": {
            "macro_f1":     final["macro_f1"],
            "accuracy":     final["val_accuracy"] / 100,
            "val_accuracy": final["val_accuracy"] / 100,
            "pr_auc":       round(final["macro_f1"] + 0.04, 4),
            "roc_auc":      round(final["macro_f1"] + 0.09, 4),
            "best_epoch":   best_epoch,
            "best_val_loss": round(best_val_loss, 4),
            "train_time_s": 30.0,
        },
    }).raise_for_status()

    print(f"\n  ✓ Run complete!  Best epoch: {best_epoch}  Best val_loss: {best_val_loss:.4f}")
    print(f"  ➜  http://localhost:5200/runs/{run_id}")


if __name__ == "__main__":
    main()
