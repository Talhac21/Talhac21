"use client";

import { useEffect, useState } from "react";
import { api, type DashboardData } from "../lib/api";

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .dashboard()
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <section><p>Loading dashboard…</p></section>;
  if (error) return <section><div className="card" style={{ color: "#f87171" }}>Error: {error}</div></section>;
  if (!data) return null;

  const jobMap = Object.fromEntries(data.jobs.map((j) => [j.account_id, j]));

  return (
    <section>
      <h2>Dashboard</h2>

      <div className="grid">
        {data.accounts.length === 0 && (
          <div className="card"><p>No accounts yet. Go to Accounts to add one.</p></div>
        )}
        {data.accounts.map((acc) => {
          const job = jobMap[acc.id];
          const statusColor = acc.session_status === "valid" ? "#4ade80" : "#f87171";
          return (
            <article key={acc.id} className="card">
              <strong>{acc.alias}</strong>
              <p>
                Session: <span style={{ color: statusColor }}>{acc.session_status}</span>
              </p>
              {job && (
                <p>
                  Auto-perk: {job.auto_enabled ? "✅ ON" : "⏸️ OFF"} · Last: {job.last_result ?? "—"} · Next:{" "}
                  {job.next_run_at ? new Date(job.next_run_at).toLocaleTimeString() : "—"}
                </p>
              )}
              {acc.last_sync_at && (
                <p style={{ fontSize: "0.85em", opacity: 0.7 }}>
                  Last sync: {new Date(acc.last_sync_at).toLocaleString()}
                </p>
              )}
            </article>
          );
        })}
      </div>

      <article className="card">
        <h3>Recent Activity</h3>
        {data.recent_logs.length === 0 ? (
          <p>No logs yet.</p>
        ) : (
          <ul style={{ listStyle: "none", padding: 0 }}>
            {data.recent_logs.map((log) => (
              <li key={log.id} style={{ marginBottom: 4, fontSize: "0.9em" }}>
                <span style={{ color: log.status === "ok" ? "#4ade80" : "#facc15" }}>
                  [{log.status}]
                </span>{" "}
                {log.action}
                {log.account_id ? ` (account #${log.account_id})` : ""}{" "}
                <span style={{ opacity: 0.5 }}>
                  {log.created_at ? new Date(log.created_at).toLocaleString() : ""}
                </span>
              </li>
            ))}
          </ul>
        )}
      </article>
    </section>
  );
}
