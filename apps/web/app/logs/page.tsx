"use client";

import { useEffect, useState } from "react";
import { api, type LogsData } from "../lib/api";

export default function LogsPage() {
  const [data, setData] = useState<LogsData | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [skip, setSkip] = useState(0);
  const limit = 50;

  const load = (offset: number) => {
    setLoading(true);
    api
      .listLogs(offset, limit)
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => load(skip), [skip]);

  if (loading) return <section><p>Loading logs…</p></section>;
  if (error) return <section><div className="card" style={{ color: "#f87171" }}>Error: {error}</div></section>;
  if (!data) return null;

  return (
    <section>
      <h2>Logs</h2>

      <article className="card">
        <h3>Audit Logs</h3>
        {data.audit.length === 0 ? (
          <p>No audit logs.</p>
        ) : (
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.85em" }}>
            <thead>
              <tr style={{ borderBottom: "1px solid #29314f" }}>
                <th style={{ textAlign: "left", padding: 4 }}>ID</th>
                <th style={{ textAlign: "left", padding: 4 }}>Action</th>
                <th style={{ textAlign: "left", padding: 4 }}>Status</th>
                <th style={{ textAlign: "left", padding: 4 }}>Account</th>
                <th style={{ textAlign: "left", padding: 4 }}>Time</th>
              </tr>
            </thead>
            <tbody>
              {data.audit.map((l) => (
                <tr key={l.id} style={{ borderBottom: "1px solid #181f35" }}>
                  <td style={{ padding: 4 }}>{l.id}</td>
                  <td style={{ padding: 4 }}>{l.action}</td>
                  <td style={{ padding: 4, color: l.status === "ok" ? "#4ade80" : "#facc15" }}>{l.status}</td>
                  <td style={{ padding: 4 }}>{l.account_id ?? "—"}</td>
                  <td style={{ padding: 4, opacity: 0.7 }}>{l.created_at ? new Date(l.created_at).toLocaleString() : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </article>

      <article className="card">
        <h3>Worker Logs</h3>
        {data.worker.length === 0 ? (
          <p>No worker logs.</p>
        ) : (
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.85em" }}>
            <thead>
              <tr style={{ borderBottom: "1px solid #29314f" }}>
                <th style={{ textAlign: "left", padding: 4 }}>ID</th>
                <th style={{ textAlign: "left", padding: 4 }}>Level</th>
                <th style={{ textAlign: "left", padding: 4 }}>Event</th>
                <th style={{ textAlign: "left", padding: 4 }}>Time</th>
              </tr>
            </thead>
            <tbody>
              {data.worker.map((w) => (
                <tr key={w.id} style={{ borderBottom: "1px solid #181f35" }}>
                  <td style={{ padding: 4 }}>{w.id}</td>
                  <td style={{ padding: 4, color: w.level === "ERROR" ? "#f87171" : "#e5e7eb" }}>{w.level}</td>
                  <td style={{ padding: 4 }}>{w.event}</td>
                  <td style={{ padding: 4, opacity: 0.7 }}>{w.created_at ? new Date(w.created_at).toLocaleString() : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </article>

      <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
        <button
          disabled={skip === 0}
          onClick={() => setSkip(Math.max(0, skip - limit))}
          style={{ padding: "6px 16px", borderRadius: 6, background: skip === 0 ? "#374151" : "#3b82f6", color: "#fff", border: "none", cursor: skip === 0 ? "default" : "pointer" }}
        >
          ← Previous
        </button>
        <button
          onClick={() => setSkip(skip + limit)}
          style={{ padding: "6px 16px", borderRadius: 6, background: "#3b82f6", color: "#fff", border: "none", cursor: "pointer" }}
        >
          Next →
        </button>
        <span style={{ alignSelf: "center", fontSize: "0.85em", opacity: 0.7 }}>
          Showing {skip + 1}–{skip + limit}
        </span>
      </div>
    </section>
  );
}
