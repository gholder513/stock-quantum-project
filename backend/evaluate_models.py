# backend/evaluate_models.py
"""
Evaluate all models (classical + quantum) on the full dataset.

Metrics:
- Accuracy vs TRUE labels
- Agreement with Random Forest baseline (treat RF as "oracle")
- Quantum model metadata: logical depth and anticipated shots
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Any
import json

import numpy as np
from sklearn.metrics import accuracy_score

from app import config
from app.data.load_data import load_or_build_all_data
from app.models.classical import (
    get_random_forest_model,
    get_logreg_model,
    get_svm_model,
)
from app.models.quantum import (
    quantum_vqc_predict,
    quantum_qnn_predict,
    MODELS_DIR,  # <- reuse same models/ directory as quantum.py
)

QUANTUM_METADATA: Dict[str, Dict[str, int]] = {
    "quantum_vqc": {
        "logical_depth": 3,
        "anticipated_shots": 1024,
    },
    "quantum_qnn": {
        "logical_depth": 4,
        "anticipated_shots": 1024,
    },
}

TRAIN_TIMES_PATH = MODELS_DIR / "train_times.json"
METRICS_PATH = MODELS_DIR / "metrics.json"


def _load_train_times() -> Dict[str, float]:
    if TRAIN_TIMES_PATH.exists():
        try:
            return json.load(TRAIN_TIMES_PATH.open("r"))
        except Exception:
            return {}
    return {}


def _predict_quantum_batch(X: np.ndarray, which: str) -> np.ndarray:
    """
    Run quantum model on each sample in X.

    which: "quantum_vqc" or "quantum_qnn"
    """
    if which == "quantum_vqc":
        qfunc = quantum_vqc_predict
    elif which == "quantum_qnn":
        qfunc = quantum_qnn_predict
    else:
        raise ValueError(f"Unknown quantum model: {which}")

    preds = []
    for i in range(X.shape[0]):
        probs = qfunc(X[i])
        decision = max(probs, key=probs.get)
        preds.append(decision)

    return np.array(preds)


def evaluate_all() -> Dict[str, Any]:
    print("Loading full dataset for evaluation...")
    df = load_or_build_all_data()

    X = df[config.FEATURE_COLS].values.astype(float)
    y_true = df["label"].values

    print(f"Total samples: {X.shape[0]}")
    print(f"Feature columns: {config.FEATURE_COLS}")
    print()

    # classical models
    print("Loading classical models (from saved .pkl files)...")
    rf = get_random_forest_model()
    logreg = get_logreg_model()
    svm = get_svm_model()

    print("Computing predictions for classical models...")
    y_rf = rf.predict(X)
    y_logreg = logreg.predict(X)
    y_svm = svm.predict(X)

    metrics: Dict[str, Dict[str, Any]] = {}

    def add_metrics(name_key: str, y_pred: np.ndarray):
        metrics.setdefault(name_key, {})
        metrics[name_key]["accuracy_vs_true"] = float(
            accuracy_score(y_true, y_pred)
        )
        metrics[name_key]["agreement_with_rf"] = float(
            accuracy_score(y_rf, y_pred)
        )

    add_metrics("random_forest", y_rf)
    add_metrics("logreg", y_logreg)
    add_metrics("svm_linear", y_svm)

    # quantum models
    print("\nRunning quantum models (this may be slower)...")
    y_vqc = _predict_quantum_batch(X, "quantum_vqc")
    y_qnn = _predict_quantum_batch(X, "quantum_qnn")

    add_metrics("quantum_vqc", y_vqc)
    add_metrics("quantum_qnn", y_qnn)

    # quantum metadata
    for q_name, meta in QUANTUM_METADATA.items():
        metrics.setdefault(q_name, {})
        metrics[q_name]["logical_depth"] = meta["logical_depth"]
        metrics[q_name]["anticipated_shots"] = meta["anticipated_shots"]

    # training times (if present)
    train_times = _load_train_times()
    for model_name, t in train_times.items():
        metrics.setdefault(model_name, {})
        metrics[model_name]["training_time_seconds"] = float(t)

    # mark RF as the baseline/oracle
    metrics.setdefault("random_forest", {})
    metrics["random_forest"]["is_baseline"] = True

    # save to JSON for the API
    METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with METRICS_PATH.open("w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Saved evaluation metrics to {METRICS_PATH}")

    return metrics


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[0]
    print(f"Running evaluation from {root}")
    evaluate_all()
