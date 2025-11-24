from typing import List

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app import config
from app.data.load_data import load_or_build_all_data
from app.models.classical import get_random_forest_model
from app.models.quantum import quantum_dummy_predict
from app.schemas import PredictionRequest, PredictionResponse

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


@app.on_event("startup")
def startup_event():
    global DATA_DF, RF_MODEL
    print("Loading data and models at startup...")
    DATA_DF = load_or_build_all_data()
    RF_MODEL = get_random_forest_model()
    print("Startup complete.")


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/tickers")
def list_tickers() -> List[str]:
    if DATA_DF is None:
        raise HTTPException(status_code=500, detail="Data not loaded")
    return sorted(DATA_DF["ticker"].unique().tolist())


@app.post("/api/predict", response_model=PredictionResponse)
def predict(req: PredictionRequest):
    if DATA_DF is None:
        raise HTTPException(status_code=500, detail="Data not loaded")

    df = DATA_DF

    # Filter for specific ticker and date
    row = df[(df["ticker"] == req.ticker) & (df["Date"] == req.date)]
    if row.empty:
        raise HTTPException(
            status_code=404,
            detail="No data for that ticker/date (might be a weekend/holiday).",
        )

    X = row[config.FEATURE_COLS].values.astype(float)

    if req.model_name == "random_forest":
        # Classical prediction
        # proba = RF_MODEL.predict_proba(X)[0]
        # classes = RF_MODEL.classes_
        # decision_idx = int(np.argmax(proba))
        # decision = classes[decision_idx]
        # probs = {cls: float(p) for cls, p in zip(classes, proba)}
        
        proba = RF_MODEL.predict_proba(X)[0]
        classes = RF_MODEL.classes_
        prob_map = {cls: float(p) for cls, p in zip(classes, proba)}

        p_buy = prob_map.get("BUY", 0.0)
        p_hold = prob_map.get("HOLD", 0.0)
        p_sell = prob_map.get("SELL", 0.0)

        # Only choose HOLD if its probability exceeds a threshold(to limit bias)
        HOLD_THRESHOLD = 0.6  # you can tune this

        if (
            p_hold >= HOLD_THRESHOLD
            and p_hold >= p_buy
            and p_hold >= p_sell
        ):
            decision = "HOLD"
        else:
            # Otherwise, commit to a direction buy vs sell,
            # ignoring hold even if it's slightly higher.
            if p_buy >= p_sell:
                decision = "BUY"
            else:
                decision = "SELL"

        probs = prob_map

    elif req.model_name == "quantum_dummy":
        # Stub quantum model – use same features, but random distribution
        probs = quantum_dummy_predict(X)
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
