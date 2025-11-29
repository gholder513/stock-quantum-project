// frontend/src/services/api.ts
export interface PredictionResponse {
  ticker: string;
  date: string;
  model_name: string;
  decision: "BUY" | "HOLD" | "SELL";
  probabilities: Record<string, number>;
}

// Base URL for the FastAPI backend.
// IMPORTANT: this must be reachable from the *browser*, so we default to localhost.
const API_BASE =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ??
  "http://localhost:8000";

async function handleResponse(res: Response) {
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`HTTP ${res.status}: ${text || res.statusText}`);
  }
  return res.json();
}

export async function fetchTickers(): Promise<string[]> {
  const res = await fetch(`${API_BASE}/api/tickers`);
  return handleResponse(res);
}

export async function getPrediction(
  ticker: string,
  date: string,
  model_name: string
): Promise<PredictionResponse> {
  const res = await fetch(`${API_BASE}/api/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ticker, date, model_name }),
  });
  return handleResponse(res);
}
