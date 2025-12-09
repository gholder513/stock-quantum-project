export interface PredictionResponse {
  ticker: string;
  date: string;
  model_name: string;
  decision: "BUY" | "HOLD" | "SELL";
  probabilities: Record<string, number>;
}

export interface ModelMetric {
  name: string;
  kind: "classical" | "quantum";
  accuracy_vs_true: number;
  agreement_with_rf: number;
  training_time_seconds?: number | null;
  logical_depth?: number | null;
  anticipated_shots?: number | null;
  is_baseline: boolean;
}

export interface MetricsResponse {
  metrics: ModelMetric[];
}

const API_BASE =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ??
  "http://localhost:8000";

async function handleResponse(response: Response) {
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`HTTP ${response.status}: ${text || response.statusText}`);
  }
  return response.json();
}

export async function fetchTickers(): Promise<string[]> {
  const response = await fetch(`${API_BASE}/api/tickers`);
  return handleResponse(response);
}

export async function getPrediction(
  ticker: string,
  date: string,
  model_name: string
): Promise<PredictionResponse> {
  const response = await fetch(`${API_BASE}/api/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ticker, date, model_name }),
  });
  return handleResponse(response);
}

export async function fetchModelMetrics(): Promise<MetricsResponse> {
  const response = await fetch(`${API_BASE}/api/model-metrics`);
  return handleResponse(response);
}
