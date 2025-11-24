import React, { useEffect, useState } from "react";
import { fetchTickers, getPrediction } from "./services/api";
import type { PredictionResponse } from "./services/api";

function App() {
  const [tickers, setTickers] = useState<string[]>([]);
  const [selectedTicker, setSelectedTicker] = useState<string>("");
  const [date, setDate] = useState<string>("2019-12-20");
  const [modelName, setModelName] = useState<string>("random_forest");
  const [result, setResult] = useState<PredictionResponse | null>(null);
  const [error, setError] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    fetchTickers()
      .then((t) => setTickers(t))
      .catch((e) => setError(e.message));
  }, []);

  const handlePredict = async () => {
    if (!selectedTicker || !date) {
      setError("Please select a ticker and a date.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const res = await getPrediction(selectedTicker, date, modelName);
      setResult(res);
    } catch (e: any) {
      setError(e.message || "Prediction failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "2rem", fontFamily: "system-ui" }}>
      <h1>Stock Decisions: Classical vs Quantum</h1>
      <p>
        Select a ticker, date, and model to get a <b>BUY / HOLD / SELL</b>{" "}
        decision.
      </p>

      {error && (
        <div style={{ color: "red", marginBottom: "1rem" }}>{error}</div>
      )}

      <div style={{ marginBottom: "1rem" }}>
        <label style={{ marginRight: "0.5rem" }}>Ticker:</label>
        <select
          value={selectedTicker}
          onChange={(e) => setSelectedTicker(e.target.value)}
        >
          <option value="">-- select --</option>
          {tickers.map((t) => (
            <option key={t} value={t}>
              {t}
            </option>
          ))}
        </select>
      </div>

      <div style={{ marginBottom: "1rem" }}>
        <label style={{ marginRight: "0.5rem" }}>Date:</label>
        <input
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
        />
        <span style={{ marginLeft: "0.5rem", fontSize: "0.85rem" }}>
          (must be a trading day between 2015–2020)
        </span>
      </div>

      <div style={{ marginBottom: "1rem" }}>
        <label style={{ marginRight: "0.5rem" }}>Model:</label>
        <select
          value={modelName}
          onChange={(e) => setModelName(e.target.value)}
        >
          <option value="random_forest">Random Forest (classical)</option>
          <option value="quantum_dummy">Quantum Dummy (stub)</option>
        </select>
      </div>

      <button onClick={handlePredict} disabled={loading}>
        {loading ? "Predicting..." : "Get Decision"}
      </button>

      {result && (
        <div style={{ marginTop: "2rem" }}>
          <h2>
            Decision:{" "}
            <span
              style={{
                color:
                  result.decision === "BUY"
                    ? "green"
                    : result.decision === "SELL"
                    ? "crimson"
                    : "orange",
              }}
            >
              {result.decision}
            </span>
          </h2>
          <p>
            <b>Ticker:</b> {result.ticker} | <b>Date:</b> {result.date} |{" "}
            <b>Model:</b> {result.model_name}
          </p>
          <h3>Probabilities</h3>
          <pre>{JSON.stringify(result.probabilities, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

export default App;
