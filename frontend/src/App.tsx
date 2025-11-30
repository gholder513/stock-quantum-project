import React, { useEffect, useState } from "react";
import { fetchTickers, getPrediction } from "./services/api";
import type { PredictionResponse } from "./services/api";
import "./App.css";

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
      setError("Please select a valid ticker and date (within 2015-2020).");
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

  const modelLabels: Record<string, string> = {
    random_forest: "Random Forest",
    logreg: "Logistic Regression",
    svm_linear: "Linear SVM",
    quantum_vqc: "Quantum VQC",
    quantum_qnn: "Quantum QNN"
  };

  return (
    <div className="quantum-container">
      <div className="hero-header">
        <div className="hero-content">
          <h1 className="main-title">Quantum Trading AI</h1>
          <div className="badges">
            <span className="badge">Quantum Computing</span>
            <span className="badge">2015-2020 Dataset</span>
            <span className="badge">5 ML Models</span>
          </div>
        </div>
      </div>

      <div className="content-wrapper">
        <div className="card">
          <h2 className="card-title">Configure Prediction</h2>
          <p className="card-subtitle">
            Select your parameters to generate AI-powered trading signals
          </p>

          {error && (
            <div className="alert alert-error">
              <span>⚠</span>
              {error}
            </div>
          )}

          <div className="form-group">
            <label className="form-label">Stock Ticker</label>
            <select
              className="form-select"
              value={selectedTicker}
              onChange={(e) => setSelectedTicker(e.target.value)}
            >
              <option value="">Choose a stock...</option>
              {tickers.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Trading Date</label>
            <input
              className="form-input"
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              min="2015-01-01"
              max="2020-12-31"
            />
            <span className="form-hint">Historical trading day (2015-2020)</span>
          </div>

          <div className="form-group">
            <label className="form-label">AI Model</label>
            <select
              className="form-select"
              value={modelName}
              onChange={(e) => setModelName(e.target.value)}
            >
              <option value="random_forest">Random Forest</option>
              <option value="logreg">Logistic Regression</option>
              <option value="svm_linear">Linear SVM</option>
              <option value="quantum_vqc">Quantum VQC (Qiskit)</option>
              <option value="quantum_qnn">Quantum QNN (PennyLane)</option>
            </select>
          </div>

          <button 
            className="btn-predict" 
            onClick={handlePredict} 
            disabled={loading}
          >
            {loading ? "Analyzing Market Data..." : "Generate Prediction"}
          </button>
        </div>

        <div className="card">
          {!result ? (
            <div className="placeholder">
              <div className="placeholder-icon">📊</div>
              <h3>Awaiting Analysis</h3>
              <p>
                Configure your parameters and click "Generate Prediction" to receive trading insights based on historical patterns and quantum algorithms.
              </p>
            </div>
          ) : (
            <>
              <div className="result-header">
                <span className="result-label">Trading Signal</span>
                <span className={`decision-badge decision-${result.decision.toLowerCase()}`}>
                  {result.decision}
                </span>
              </div>

              <div className="meta-grid">
                <div className="meta-item">
                  <div className="meta-label">Ticker</div>
                  <div className="meta-value">{result.ticker}</div>
                </div>
                <div className="meta-item">
                  <div className="meta-label">Date</div>
                  <div className="meta-value">{result.date}</div>
                </div>
                <div className="meta-item">
                  <div className="meta-label">Model</div>
                  <div className="meta-value">{modelLabels[result.model_name]}</div>
                </div>
              </div>

              <div className="probabilities-section">
                <h3>Probability Distribution</h3>
                {Object.entries(result.probabilities).map(([label, value]) => (
                  <div key={label} className="prob-item">
                    <div className="prob-header">
                      <span className="prob-label">{label}</span>
                      <span className="prob-value">{(value * 100).toFixed(1)}%</span>
                    </div>
                    <div className="prob-bar">
                      <div className="prob-fill" style={{ width: `${value * 100}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;