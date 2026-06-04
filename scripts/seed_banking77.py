"""
Seed script — imports Banking77 SVM and MLP results from the CSCI 581 project
as the first two tracked experiments in the ML Experiment Tracker.

Usage:
    cd ml-experiment-tracker
    python scripts/seed_banking77.py --api-url http://localhost:8000
"""
import argparse
import json
import time

import httpx

SVM_METRICS_BY_EPOCH = [
    # SVM does not have epochs — represent as a single "epoch 0" final result
    {"step": 0, "metrics": {"macro_f1": 0.8862, "pr_auc": 0.9228, "roc_auc": 0.9951, "accuracy": 0.8859}},
]

MLP_METRICS_BY_EPOCH = [
    {"step": 1,  "metrics": {"loss": 4.1234, "val_loss": 2.9635, "accuracy": 4.31,  "val_accuracy": 11.05}},
    {"step": 2,  "metrics": {"loss": 2.9635, "val_loss": 1.5118, "accuracy": 16.37, "val_accuracy": 51.15}},
    {"step": 3,  "metrics": {"loss": 1.5118, "val_loss": 0.9077, "accuracy": 41.33, "val_accuracy": 76.36}},
    {"step": 4,  "metrics": {"loss": 0.9077, "val_loss": 0.6778, "accuracy": 60.69, "val_accuracy": 82.22}},
    {"step": 5,  "metrics": {"loss": 0.6778, "val_loss": 0.5967, "accuracy": 72.07, "val_accuracy": 84.77}},
    {"step": 6,  "metrics": {"loss": 0.5967, "val_loss": 0.5594, "accuracy": 79.57, "val_accuracy": 85.28}},
    {"step": 7,  "metrics": {"loss": 0.5594, "val_loss": 0.5449, "accuracy": 84.48, "val_accuracy": 85.33}},
    {"step": 8,  "metrics": {"loss": 0.5449, "val_loss": 0.5416, "accuracy": 87.69, "val_accuracy": 85.48}},
    {"step": 9,  "metrics": {"loss": 0.5332, "val_loss": 0.5332, "accuracy": 89.18, "val_accuracy": 85.53}},  # best
    {"step": 10, "metrics": {"loss": 0.4912, "val_loss": 0.5333, "accuracy": 91.36, "val_accuracy": 85.48}},
    {"step": 11, "metrics": {"loss": 0.4201, "val_loss": 0.5354, "accuracy": 92.88, "val_accuracy": 85.63}},
    {"step": 12, "metrics": {"loss": 0.3870, "val_loss": 0.5418, "accuracy": 93.54, "val_accuracy": 85.28}},
    {"step": 13, "metrics": {"loss": 0.3201, "val_loss": 0.5512, "accuracy": 94.62, "val_accuracy": 85.58}},
    {"step": 14, "metrics": {"loss": 0.2980, "val_loss": 0.5567, "accuracy": 94.77, "val_accuracy": 85.84}},
    {"step": 15, "metrics": {"loss": 0.2650, "val_loss": 0.5661, "accuracy": 95.47, "val_accuracy": 85.74}},
    {"step": 16, "metrics": {"loss": 0.2512, "val_loss": 0.5730, "accuracy": 95.57, "val_accuracy": 86.35}},
    {"step": 17, "metrics": {"loss": 0.2301, "val_loss": 0.5901, "accuracy": 95.85, "val_accuracy": 85.79}},
    {"step": 18, "metrics": {"loss": 0.1980, "val_loss": 0.5857, "accuracy": 96.70, "val_accuracy": 85.89}},
    {"step": 19, "metrics": {"loss": 0.2010, "val_loss": 0.6000, "accuracy": 96.56, "val_accuracy": 86.04}},
]


def seed(api_url: str):
    client = httpx.Client(base_url=api_url, timeout=10.0)

    print("Seeding Banking77 SVM run...")
    svm_run = client.post("/api/v1/runs", json={
        "name": "banking77-svm-linearSVC",
        "model_type": "LinearSVC",
        "dataset": "banking77",
        "hyperparams": {"C": 1.0, "cv_folds": 5, "ngram_range": "(1,2)", "max_features": 10000},
        "tags": ["svm", "tfidf", "banking77", "baseline"],
        "notes": "CSCI 581 Final Project — SVM baseline. Grid search over C∈{0.1,1.0,10.0}. Best C=1.0, CV F1=0.8799.",
    }).raise_for_status().json()
    svm_id = svm_run["id"]

    for m in SVM_METRICS_BY_EPOCH:
        client.post(f"/api/v1/runs/{svm_id}/metrics", json=m).raise_for_status()

    client.patch(f"/api/v1/runs/{svm_id}", json={
        "status": "completed",
        "final_metrics": {"macro_f1": 0.8862, "pr_auc": 0.9228, "roc_auc": 0.9951, "accuracy": 0.8859, "train_time_s": 3.67},
    }).raise_for_status()
    print(f"  SVM run created: {svm_id}")

    print("Seeding Banking77 MLP run (19 epochs)...")
    mlp_run = client.post("/api/v1/runs", json={
        "name": "banking77-deep-mlp",
        "model_type": "DeepMLP",
        "dataset": "banking77",
        "hyperparams": {"lr": 0.001, "epochs": 100, "batch_size": 256, "dropout": 0.3,
                        "hidden_layers": [256, 128, 64], "optimizer": "Adam", "early_stopping_patience": 10},
        "tags": ["mlp", "keras", "tfidf", "banking77"],
        "notes": "CSCI 581 Final Project — Deep MLP. EarlyStopping at epoch 19, best epoch 9 (val_loss=0.5332).",
    }).raise_for_status().json()
    mlp_id = mlp_run["id"]

    for m in MLP_METRICS_BY_EPOCH:
        client.post(f"/api/v1/runs/{mlp_id}/metrics", json=m).raise_for_status()
        time.sleep(0.05)  # slight delay to preserve order

    client.patch(f"/api/v1/runs/{mlp_id}", json={
        "status": "completed",
        "final_metrics": {"macro_f1": 0.8599, "pr_auc": 0.9244, "roc_auc": 0.9960, "accuracy": 0.8599,
                          "train_time_s": 13.60, "best_epoch": 9, "best_val_loss": 0.5332},
    }).raise_for_status()
    print(f"  MLP run created: {mlp_id}")

    print("\nSeed complete!")
    print(f"  SVM: http://localhost:5173/runs/{svm_id}")
    print(f"  MLP: http://localhost:5173/runs/{mlp_id}")
    print(f"  Compare: http://localhost:5173/compare?ids={svm_id},{mlp_id}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-url", default="http://localhost:8000")
    args = parser.parse_args()
    seed(args.api_url)
