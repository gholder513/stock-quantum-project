from typing import List

import numpy as np
import pandas as pd
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

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
    MODELS_DIR,
)
from app.schemas import (
    PredictionRequest,
    PredictionResponse,
    MetricsResponse,
    ModelMetric,
)
app = FastAPI(title="Stock Quantum Project API")

# Allow local frontend (Vite dev server)
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


DATA_DF: pd.DataFrame | None = None
RF_MODEL = None
LOGREG_MODEL = None
SVM_MODEL = None
METRICS_PATH = MODELS_DIR / "metrics.json"


def ensure_data_and_models_loaded() -> None:
    """
    Lazy-load data and classical models if they haven't been loaded yet.
    This makes the API robust even if the startup event didn't preload them.
    """
    global DATA_DF, RF_MODEL, LOGREG_MODEL, SVM_MODEL

    if DATA_DF is None:
        print("Lazy-loading data...")
        DATA_DF = load_or_build_all_data()

    if RF_MODEL is None:
        print("Lazy-loading Random Forest model...")
        RF_MODEL = get_random_forest_model()

    if LOGREG_MODEL is None:
        print("Lazy-loading Logistic Regression model...")
        LOGREG_MODEL = get_logreg_model()

    if SVM_MODEL is None:
        print("Lazy-loading Linear SVM model...")
        SVM_MODEL = get_svm_model()


@app.on_event("startup")
def startup_event() -> None:
    """
    Don't load anything at startup to save memory.
    Models will be loaded on first request via ensure_data_and_models_loaded().
    """
    print("Startup event: Skipping preload to conserve memory.")
    print("Models and data will be loaded on first API request.")


@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/api/model-metrics", response_model=MetricsResponse)
def get_model_metrics():
    if not METRICS_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="Model metrics not found. Run evaluate_models.py first.",
        )

    try:
        raw = json.load(METRICS_PATH.open("r"))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to read metrics.json: {e!r}",
        )

    metrics_list: list[ModelMetric] = []
    for name, data in raw.items():
        kind = "quantum" if name.startswith("quantum_") else "classical"
        metrics_list.append(
            ModelMetric(
                name=name,
                kind=kind,
                accuracy_vs_true=float(data.get("accuracy_vs_true", 0.0)),
                agreement_with_rf=float(data.get("agreement_with_rf", 0.0)),
                training_time_seconds=data.get("training_time_seconds"),
                logical_depth=data.get("logical_depth"),
                anticipated_shots=data.get("anticipated_shots"),
                is_baseline=bool(data.get("is_baseline", False)),
            )
        )

    return MetricsResponse(metrics=metrics_list)

@app.get("/api/tickers")
def list_tickers() -> List[str]:
    ensure_data_and_models_loaded()
    # DATA_DF is guaranteed non-None after ensure_data_and_models_loaded()
    return sorted(DATA_DF["ticker"].unique().tolist())  # type: ignore[union-attr]


def _predict_with_hold_threshold(model, X: np.ndarray, hold_threshold: float = 0.6):
    """
    Shared logic for classical models:
    - Get class probabilities via predict_proba
    - Apply HOLD-threshold rule to reduce HOLD bias
    """
    proba = model.predict_proba(X)[0]
    classes = model.classes_
    prob_map = {cls: float(p) for cls, p in zip(classes, proba)}

    p_buy = prob_map.get("BUY", 0.0)
    p_hold = prob_map.get("HOLD", 0.0)
    p_sell = prob_map.get("SELL", 0.0)

    if (
        p_hold >= hold_threshold
        and p_hold >= p_buy
        and p_hold >= p_sell
    ):
        decision = "HOLD"
    else:
        decision = "BUY" if p_buy >= p_sell else "SELL"

    return decision, prob_map


@app.post("/api/predict", response_model=PredictionResponse)
def predict(req: PredictionRequest):
    ensure_data_and_models_loaded()

    df = DATA_DF  # type: ignore[assignment]
    if df is None:
        raise HTTPException(status_code=500, detail="Data not loaded")

    # Filter for specific ticker and date
    row = df[(df["ticker"] == req.ticker) & (df["Date"] == req.date)]
    if row.empty:
        raise HTTPException(
            status_code=404,
            detail="No data for that ticker/date (might be a weekend/holiday).",
        )

    # Extract features
    X = row[config.FEATURE_COLS].values.astype(float)

    # Dispatch based on model_name
    if req.model_name == "random_forest":
        decision, probs = _predict_with_hold_threshold(RF_MODEL, X)

    elif req.model_name == "logreg":
        decision, probs = _predict_with_hold_threshold(LOGREG_MODEL, X)

    elif req.model_name == "svm_linear":
        decision, probs = _predict_with_hold_threshold(SVM_MODEL, X)

    elif req.model_name == "quantum_vqc":
        probs = quantum_vqc_predict(X)
        decision = max(probs, key=probs.get)

    elif req.model_name == "quantum_qnn":
        probs = quantum_qnn_predict(X)
        decision = max(probs, key=probs.get)

    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown model_name: {req.model_name}",
        )

    return PredictionResponse(
        ticker=req.ticker,
        date=req.date,
        model_name=req.model_name,
        decision=decision,
        probabilities=probs,
    )