import { useEffect, useState } from "react";
import { fetchTickers, getPrediction } from "./services/api";
import type { PredictionResponse } from "./services/api";
import "./App.css";
import { ModelMetricsPanel } from "./components/ModelMetricsPanel";
import Editor from "@monaco-editor/react";

function App() {
  const [tickers, setTickers] = useState<string[]>([]);
  const [selectedTicker, setSelectedTicker] = useState<string>("");
  const [date, setDate] = useState<string>("2019-12-20");
  const [modelName, setModelName] = useState<string>("random_forest");
  const [result, setResult] = useState<PredictionResponse | null>(null);
  const [error, setError] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [comparisonResults, setComparisonResults] = useState<
    PredictionResponse[] | null
  >(null);
  const [comparing, setComparing] = useState(false);

  useEffect(() => {
    fetchTickers()
      .then((t) => setTickers(t))
      .catch((e) => setError(e.message));
  }, []);

  const handlePredict = async () => {
    setComparing(false);
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
    quantum_qnn: "Quantum QNN",
  };

  const handleCompare = async () => {
    if (!selectedTicker || !date) return;

    setComparing(true);
    setComparisonResults(null);

    const otherModels = [
      "random_forest",
      "logreg",
      "svm_linear",
      "quantum_vqc",
      "quantum_qnn",
    ].filter((m) => m !== modelName); // exclude current selected model

    try {
      const predictions = await Promise.all(
        otherModels.map((model) => getPrediction(selectedTicker, date, model))
      );
      setComparisonResults(predictions);
    } catch (e: any) {
      console.error("Comparison failed", e);
      setComparing(false);
    }
  };

  return (
    <div className="quantum-container">
      <div className="hero-header">
        <div className="hero-content">
          <h1 className="main-title">Quantum Trading AI</h1>

          {/* Landing-page experiment sentence (verbatim first part) */}
          <p className="subtitle">
            Simulated highly volatile stock trading based on futures
            calculated on a 2 day look-ahead window. We use a buy and sell
            threshold of +- 1%. The point of the study is to compare the
            accuracy of traditional ML algorithms against a 2-qubit
            parameterized circuit when the dataset is extremely condensed and
            data is sparse(5 year window).
          </p>

          <div className="badges">
            <span className="badge">Quantum Computing</span>
            <span className="badge">2015-2020 Dataset</span>
            <span className="badge">5 ML Models</span>
          </div>

          {/* Small hero metric cards */}
          <div className="hero-meta">
            <div className="hero-pill">
              <span className="hero-pill-label">Look-ahead horizon</span>
              <span className="hero-pill-value">2-day futures window</span>
            </div>
            <div className="hero-pill">
              <span className="hero-pill-label">Trading regime</span>
              <span className="hero-pill-value">
                ±1% intraday BUY / SELL threshold
              </span>
            </div>
            <div className="hero-pill">
              <span className="hero-pill-label">Models compared</span>
              <span className="hero-pill-value">
                RF, LogReg, SVM, Quantum VQC, Quantum QNN
              </span>
            </div>
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
            <span className="form-hint">
              Historical trading day (2015-2020)
            </span>
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
                Configure your parameters and click "Generate Prediction" to
                receive trading insights based on historical patterns and
                quantum algorithms.
              </p>
            </div>
          ) : (
            <>
              <div className="result-header">
                <span className="result-label">Trading Signal</span>
                <span
                  className={`decision-badge decision-${result.decision.toLowerCase()}`}
                >
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
                  <div className="meta-value">
                    {modelLabels[result.model_name]}
                  </div>
                </div>
              </div>

              <div className="probabilities-section">
                <h3>Probability Distribution</h3>
                {Object.entries(result.probabilities).map(([label, value]) => (
                  <div key={label} className="prob-item">
                    <div className="prob-header">
                      <span className="prob-label">{label}</span>
                      <span className="prob-value">
                        {(value * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="prob-bar">
                      <div
                        className="prob-fill"
                        style={{ width: `${value * 100}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>

              {result && !comparing && (
                <button className="btn-predict mt-4" onClick={handleCompare}>
                  Compare Other Models
                </button>
              )}

              {result && comparing && (
                <button
                  className="btn-predict mt-4"
                  onClick={() => {
                    setComparing(false);
                    setComparisonResults(null);
                  }}
                >
                  Stop Comparing
                </button>
              )}
            </>
          )}
        </div>
      </div>

      {comparisonResults && comparing && (
        <div className="content-wrapper2">
          <div className="comparison-row">
            {comparisonResults.map((res) => (
              <div key={res.model_name} className="card comparison-card">
                <div className="result-header">
                  <span className="result-label">Trading Signal</span>
                  <span
                    className={`decision-badge decision-${res.decision.toLowerCase()}`}
                  >
                    {res.decision}
                  </span>
                </div>

                <div className="meta-grid">
                  <div className="meta-item">
                    <div className="meta-label">Ticker</div>
                    <div className="meta-value">{res.ticker}</div>
                  </div>
                  <div className="meta-item">
                    <div className="meta-label">Date</div>
                    <div className="meta-value">{res.date}</div>
                  </div>
                  <div className="meta-item">
                    <div className="meta-label">Model</div>
                    <div className="meta-value">
                      {modelLabels[res.model_name]}
                    </div>
                  </div>
                </div>

                <div className="probabilities-section">
                  <h3>Probability Distribution</h3>
                  {Object.entries(res.probabilities).map(([label, value]) => (
                    <div key={label} className="prob-item">
                      <div className="prob-header">
                        <span className="prob-label">{label}</span>
                        <span className="prob-value">
                          {(value * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="prob-bar">
                        <div
                          className="prob-fill"
                          style={{ width: `${value * 100}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Technical details / write-up section */}
      <section className="research-section">
        <div className="card research-main-card">
          <h2 className="card-title">Technical Details</h2>
          <p className="card-subtitle">
            Full description of how the dataset, features, classical baselines,
            and quantum models fit together.
          </p>

          {/* TEXT ABOVE EDITOR (verbatim) */}
          <div className="research-text-block">
            <p>
              Highly volatile stock trading based on futures
              calculated on a two day look-ahead window. We use a buy and sell
              threshold of +- 1%. The point of the study is to compare the
              accuracy of traditional ML algorithms against a 2-qubit
              parameterized circuit when the dataset is extremely condensed and
              data is sparse(5 year window). This task is acomplished using
              features(the same ones we used for our classical models,
              Supported Vector Machine, logistic regression and Random Forest)
              and simulated its state vector using Qiskit. From there probabilities are derived. 
              For the Quantum neural network we used pennylane’s rotational and entaglement methods
              available to simulated actual qubits and had those act
              as the layers with weights that continuously got updated as the model trained. In terms of
              the features we chose our yahoo finance dataset had a couple handy
              metrics but overall it was generally limited in scope of what we
              could derive from one dataset. I chose to prioritize a few
              features and potentially expand on them later if I choose to come
              back to the project in the future. We had:
            </p>
            <p style={{ marginTop: "0.75rem" }}>
              Date,Adj Close,Close,High,Low,Open,Volume,ticker
              <br />
              From our dataset. As a part of preprocessing I calculated the
              following features to use in the project:
            </p>
          </div>

          {/* MONACO EDITOR – ONLY THE CODE BLOCK */}
          <div className="monaco-wrapper">
            <Editor
              height="260px"
              defaultLanguage="python"
              theme="vs-dark"
              options={{
                minimap: { enabled: false },
                scrollBeyondLastLine: false,
                fontSize: 13,
                lineNumbers: "on",
              }}
              defaultValue={`vol = df["Volume"]
    if isinstance(vol, pd.DataFrame):
        vol = vol.iloc[:, 0]

    df["Adj Close"] = pd.to_numeric(adj, errors="coerce")
    df["Volume"] = pd.to_numeric(vol, errors="coerce")

    # Daily return
    df["daily_return"] = df["Adj Close"].pct_change()

    # Moving averages
    df["ma_5"] = df["Adj Close"].rolling(window=5, min_periods=5).mean()
    df["ma_10"] = df["Adj Close"].rolling(window=10, min_periods=10).mean()

    # Momentum (14-day simple momentum)
    df["momentum_14"] = df["Adj Close"] - df["Adj Close"].shift(14)

    # Volume z-score over last 20 days
    vol_rolling_mean = df["Volume"].rolling(window=20, min_periods=20).mean()
    vol_rolling_std = df["Volume"].rolling(window=20, min_periods=20).std()
    df["volume_zscore_20"] = (df["Volume"] - vol_rolling_mean) / vol_rolling_std.replace(
        0, np.nan
    )`}
            />
          </div>

          
          <div className="research-text-block" style={{ marginTop: "1.25rem" }}>
            <p>
              These are the features the models trained on without knowing the
              labels. Also preprocessed the labels for the sake of simplicity
              and based it on future returns and simulated a day trading
              environment making decisions to buy or sell on a 1% margin gain
              or loss. It’s important to note when looking at the accuracy of
              the models that these were designed for variance. NASDAQ
              companies having major fluctuations on a day to day basis of many
              percentage points is unlikely due to their standing.
            </p>

            <p style={{ marginTop: "0.75rem" }}>
              The metrics reflect that random forest’s performance was by far
              the best getting an accuracy of 92% with the lowest training time.
              The QNN Quantum Neural Network performance proved to be on par
              with the other classical models. With more fine-tuning on features
              alone I’m sure we could get almost all models above 80% accuracy.
            </p>

            <p style={{ marginTop: "0.75rem" }}>
              In the future with this project I want to explore time series
              forecasting just for personal experimentation. An implementation
              would likely look like using Darts library with ARIMA or Meta’s
              prophet model(I’ve heard good things about that) and potentially
              using GARCH for some volatile forecasting for side metrics.
            </p>

            <p style={{ marginTop: "0.75rem" }}>Enjoy the app!</p>
          </div>
        </div>

        {/* Side cards: feature snapshot + model comparison */}
        <div className="research-grid">
          <div className="card info-card">
            <h3 className="card-title">Feature Engineering Snapshot</h3>
            <p className="card-subtitle">
              Core OHLCV fields are transformed into momentum, moving averages,
              and volume anomalies before feeding models.
            </p>
            <pre className="code-block">
{`# Core engineered signals
df["daily_return"]   # 1-day log-style return
df["ma_5"]           # 5-day moving average
df["ma_10"]          # 10-day moving average
df["momentum_14"]    # 14-day simple momentum
df["volume_zscore_20"]  # 20-day z-scored volume spike detector`}
            </pre>
            <ul className="feature-list">
              <li>Condensed 5-year window of NASDAQ-like tickers (2015–2020).</li>
              <li>
                Signals intentionally tuned for volatility in an otherwise
                stable, large-cap universe.
              </li>
              <li>
                Labels derived from ±1% forward returns to emulate intraday
                decision-making.
              </li>
            </ul>
          </div>

          <div className="card info-card">
            <h3 className="card-title">Model Comparison at a Glance</h3>
            <p className="card-subtitle">
              Random Forest is the efficiency benchmark; quantum models stay
              competitive on a sparse, engineered feature space.
            </p>

            <div className="metric-grid">
              <div className="metric-row">
                <div className="metric-header">
                  <span className="metric-label">
                    Classical Random Forest{" "}
                    <span className="metric-tag">Best accuracy</span>
                  </span>
                  <span className="metric-value">91.8%</span>
                </div>
                <div className="metric-bar">
                  <div className="metric-fill" style={{ width: "91.8%" }} />
                </div>
              </div>

              <div className="metric-row">
                <div className="metric-header">
                  <span className="metric-label">
                    Classical Logistic Regression
                  </span>
                  <span className="metric-value">63.3%</span>
                </div>
                <div className="metric-bar">
                  <div className="metric-fill" style={{ width: "63.3%" }} />
                </div>
              </div>

              <div className="metric-row">
                <div className="metric-header">
                  <span className="metric-label">Classical Linear SVM</span>
                  <span className="metric-value">63.1%</span>
                </div>
                <div className="metric-bar">
                  <div className="metric-fill" style={{ width: "63.1%" }} />
                </div>
              </div>

              <div className="metric-row">
                <div className="metric-header">
                  <span className="metric-label">Quantum VQC</span>
                  <span className="metric-value">14.5%</span>
                </div>
                <div className="metric-bar">
                  <div className="metric-fill" style={{ width: "14.5%" }} />
                </div>
              </div>

              <div className="metric-row">
                <div className="metric-header">
                  <span className="metric-label">
                    Quantum QNN{" "}
                    <span className="metric-tag">On par w/ classical</span>
                  </span>
                  <span className="metric-value">63.1%</span>
                </div>
                <div className="metric-bar">
                  <div className="metric-fill" style={{ width: "63.1%" }} />
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <ModelMetricsPanel />
    </div>
  );
}

export default App;
