"""
Example: track a Keras/TensorFlow MLP using the SDK + KerasCallback.

Run from the ml-experiment-tracker root:
    python sdk/examples/track_keras.py
"""
import sys
sys.path.insert(0, "sdk")

import ml_tracker
from ml_tracker.callbacks import KerasCallback

# ── Your real model here ───────────────────────────────────────────────────────
# from tensorflow import keras
# model = keras.Sequential([...])
# model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])

run = ml_tracker.init(
    name="mlp-sdk-keras-demo",
    model_type="DeepMLP",
    dataset="banking77",
    hyperparams={
        "lr": 0.001,
        "epochs": 50,
        "batch_size": 256,
        "dropout": 0.3,
        "hidden_layers": [256, 128, 64],
        "optimizer": "Adam",
        "early_stopping_patience": 10,
    },
    tags=["mlp", "keras", "sdk-demo", "banking77"],
)

print(f"Run created: http://localhost:5200/runs/{run.id}")
print("Pass KerasCallback(run) to model.fit():")
print()
print("  model.fit(")
print("      X_train, y_train,")
print("      validation_data=(X_val, y_val),")
print("      epochs=50,")
print("      callbacks=[KerasCallback(run)],  # <-- this is all you need")
print("  )")

# Simulate what KerasCallback does internally (no TF needed for this demo):
import math, random
random.seed(7)
for epoch in range(1, 21):
    p = epoch / 20
    metrics = {
        "loss":         round(3.5 * math.exp(-3.5*p) + 0.18 + random.gauss(0, 0.02), 4),
        "val_loss":     round(3.5 * math.exp(-3.0*p) + 0.26 + random.gauss(0, 0.03), 4),
        "accuracy":     round((1 - math.exp(-4.0*p)) * 91.0 + random.gauss(0, 0.5), 2),
        "val_accuracy": round((1 - math.exp(-3.5*p)) * 87.0 + random.gauss(0, 0.7), 2),
    }
    run.log(metrics, step=epoch)
    print(f"  epoch {epoch:2d}  loss={metrics['loss']:.4f}  val_acc={metrics['val_accuracy']:.1f}%")

run.finish(final_metrics={
    "macro_f1":   0.8599,
    "accuracy":   0.8599,
    "pr_auc":     0.9244,
    "roc_auc":    0.9960,
    "best_epoch": 9,
    "train_time_s": 13.60,
})

print(f"\nDone!  http://localhost:5200/runs/{run.id}")
