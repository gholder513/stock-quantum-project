from typing import Dict, Literal, Optional, List

from pydantic import BaseModel

# Core prediction schemas (what you already had)
Decision = Literal["BUY", "HOLD", "SELL"]


class PredictionRequest(BaseModel):
    ticker: str
    date: str              # "YYYY-MM-DD"
    # Supported values in your current backend:
    # "random_forest", "logreg", "svm_linear", "quantum_vqc", "quantum_qnn"
    model_name: str


class PredictionResponse(BaseModel):
    ticker: str
    date: str
    model_name: str
    decision: Decision
    probabilities: Dict[str, float]


# New schemas for model evaluation metrics
class ModelMetric(BaseModel):
    name: str                     # e.g. "random_forest", "quantum_qnn"
    kind: Literal["classical", "quantum"]
    accuracy_vs_true: float       # accuracy vs TRUE labels
    agreement_with_rf: float      # agreement with RF "oracle"
    training_time_seconds: Optional[float] = None
    logical_depth: Optional[int] = None          # quantum-only
    anticipated_shots: Optional[int] = None      # quantum-only
    is_baseline: bool = False     # True for RF baseline


class MetricsResponse(BaseModel):
    metrics: List[ModelMetric]
