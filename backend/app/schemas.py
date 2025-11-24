from typing import Dict, Literal

from pydantic import BaseModel

Decision = Literal["BUY", "HOLD", "SELL"]


class PredictionRequest(BaseModel):
    ticker: str
    date: str              # "YYYY-MM-DD"
    model_name: str        # "random_forest" or "quantum_dummy"


class PredictionResponse(BaseModel):
    ticker: str
    date: str
    model_name: str
    decision: Decision
    probabilities: Dict[str, float]
