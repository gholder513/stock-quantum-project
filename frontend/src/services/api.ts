export interface PredictionResponse {
  ticker: string;
  date: string;
  model_name: string;
  decision: "BUY" | "HOLD" | "SELL";
  probabilities: Record<string, number>;
}

export async function fetchTickers(): Promise<string[]> {
  const res = await fetch("http://localhost:8000/api/tickers");
  if (!res.ok) {
    throw new Error("Failed to fetch tickers");
  }
  return res.json();
}

export async function getPrediction(
  ticker: string,
  date: string,
  modelName: string
): Promise<PredictionResponse> {
  const res = await fetch("http://localhost:8000/api/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ticker, date, model_name: modelName }),
  });

  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(
      `Prediction failed (${res.status}): ${errorText || "Unknown error"}`
    );
  }

  return res.json();
}
