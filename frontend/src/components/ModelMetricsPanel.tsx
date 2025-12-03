// frontend/src/components/ModelMetricsPanel.tsx
import { useEffect, useState } from "react";
import { fetchModelMetrics } from "../services/api";
import type { ModelMetric } from "../services/api";

export function ModelMetricsPanel() {
  const [metrics, setMetrics] = useState<ModelMetric[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const res = await fetchModelMetrics();
        setMetrics(res.metrics);
      } catch (err: any) {
        setError(err?.message ?? "Failed to load model metrics");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) {
    return (
      <div className="mt-4 text-sm text-gray-500">Loading model metrics…</div>
    );
  }

  if (error) {
    return (
      <div className="mt-4 text-sm text-red-500">
        Error loading model metrics: {error}
      </div>
    );
  }

  if (!metrics.length) {
    return (
      <div className="mt-4 text-sm text-gray-500">
        No metrics found. Have you run <code>evaluate_models.py</code>?
      </div>
    );
  }

  return (
    <div className="metrics-card">
      <h2>Model Performance & Quantum Metadata</h2>

      <div className="overflow-x-auto">
        <table>
          <thead>
            <tr>
              <th>Model</th>
              <th>Type</th>
              <th>Acc vs TRUE</th>
              <th>Agree w/ RF</th>
              <th>Train Time (s)</th>
              <th>Logical Depth</th>
              <th>Shots</th>
            </tr>
          </thead>
          <tbody>
            {metrics.map((m) => (
              <tr key={m.name}>
                <td>
                  {m.name}
                  {m.is_baseline && (
                    <span className="baseline-badge">baseline</span>
                  )}
                </td>
                <td>{m.kind}</td>
                <td>{m.accuracy_vs_true.toFixed(3)}</td>
                <td>{m.agreement_with_rf.toFixed(3)}</td>
                <td>{m.training_time_seconds?.toFixed(3) ?? "—"}</td>
                <td>{m.logical_depth ?? "—"}</td>
                <td>{m.anticipated_shots ?? "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <p className="text-xs text-gray-500 mt-4">
        * Agreement with RF uses Random Forest as the baseline "oracle" model.
      </p>
    </div>
  );
}
