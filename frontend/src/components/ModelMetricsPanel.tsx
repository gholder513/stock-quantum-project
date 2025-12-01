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
    return <div className="mt-4 text-sm text-gray-500">Loading model metrics…</div>;
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
    <div className="mt-6 border rounded-xl p-4 shadow-sm bg-white">
      <h2 className="text-lg font-semibold mb-3">
        Model Performance & Quantum Metadata
      </h2>
      <div className="overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead>
            <tr className="border-b">
              <th className="text-left py-1 pr-4">Model</th>
              <th className="text-left py-1 pr-4">Type</th>
              <th className="text-right py-1 pr-4">Acc vs TRUE</th>
              <th className="text-right py-1 pr-4">Agree w/ RF</th>
              <th className="text-right py-1 pr-4">Train Time (s)</th>
              <th className="text-right py-1 pr-4">Logical Depth</th>
              <th className="text-right py-1 pr-4">Shots</th>
            </tr>
          </thead>
          <tbody>
            {metrics.map((m) => (
              <tr key={m.name} className="border-b last:border-0">
                <td className="py-1 pr-4">
                  {m.name}
                  {m.is_baseline && (
                    <span className="ml-2 text-xs px-2 py-0.5 rounded-full bg-blue-100 text-blue-700">
                      baseline
                    </span>
                  )}
                </td>
                <td className="py-1 pr-4 capitalize">{m.kind}</td>
                <td className="py-1 pr-4 text-right">
                  {m.accuracy_vs_true.toFixed(3)}
                </td>
                <td className="py-1 pr-4 text-right">
                  {m.agreement_with_rf.toFixed(3)}
                </td>
                <td className="py-1 pr-4 text-right">
                  {m.training_time_seconds != null
                    ? m.training_time_seconds.toFixed(3)
                    : "—"}
                </td>
                <td className="py-1 pr-4 text-right">
                  {m.logical_depth ?? "—"}
                </td>
                <td className="py-1 pr-4 text-right">
                  {m.anticipated_shots ?? "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="mt-2 text-xs text-gray-500">
        * Agreement with RF uses Random Forest as the baseline "oracle" model.
      </p>
    </div>
  );
}
