from pathlib import Path
import time
import json

from app.models.classical import (
    train_and_save_random_forest,
    train_and_save_logreg,
    train_and_save_svm_linear,
)

ROOT_DIR = Path(__file__).resolve().parents[1]
MODELS_DIR = ROOT_DIR / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

TRAIN_TIMES_PATH = MODELS_DIR / "train_times.json"


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[0]
    print(f"Running classical retraining from {root}")

    train_times = {}

    #  Random Forest 
    t0 = time.time()
    train_and_save_random_forest()
    t_rf = time.time() - t0
    print(f"[Timing] Random Forest training time: {t_rf:.3f} seconds")
    train_times["random_forest"] = t_rf

    #  Logistic Regression 
    t0 = time.time()
    train_and_save_logreg()
    t_lr = time.time() - t0
    print(f"[Timing] Logistic Regression training time: {t_lr:.3f} seconds")
    train_times["logreg"] = t_lr

    #  Linear SVM 
    t0 = time.time()
    train_and_save_svm_linear()
    t_svm = time.time() - t0
    print(f"[Timing] Linear SVM training time: {t_svm:.3f} seconds")
    train_times["svm_linear"] = t_svm

    # Merge with any existing times (e.g., quantum)
    if TRAIN_TIMES_PATH.exists():
        try:
            existing = json.load(TRAIN_TIMES_PATH.open("r"))
        except Exception:
            existing = {}
    else:
        existing = {}

    existing.update(train_times)
    with TRAIN_TIMES_PATH.open("w") as f:
        json.dump(existing, f, indent=2)

    print(f"[Timing] Saved training times to {TRAIN_TIMES_PATH}")
