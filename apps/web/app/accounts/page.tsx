"use client";

import { useEffect, useState } from "react";
import { api, type Account, type PerkRunResult } from "../lib/api";

export default function AccountsPage() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [alias, setAlias] = useState("");
  const [sessionJson, setSessionJson] = useState("");
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const reload = () => {
    api
      .listAccounts()
      .then(setAccounts)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  };

  useEffect(reload, []);

  const handleCreate = async () => {
    if (!alias.trim()) return;
    setError("");
    setMessage("");
    try {
      await api.createAccount(alias.trim());
      setAlias("");
      setMessage("Account created!");
      reload();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    }
  };

  const handleBootstrap = async () => {
    if (!selectedId || !sessionJson.trim()) return;
    setError("");
    setMessage("");
    try {
      await api.bootstrapSession(selectedId, sessionJson.trim());
      setSessionJson("");
      setMessage("Session bootstrapped!");
      reload();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    }
  };

  const handleRunPerk = async (accountId: number) => {
    setError("");
    setMessage("");
    try {
      const result: PerkRunResult = await api.runPerkNow(accountId);
      setMessage(
        `Perk: ${result.success ? "✅" : "❌"} ${result.message}${result.next_run_at ? ` · Next: ${new Date(result.next_run_at).toLocaleTimeString()}` : ""}`
      );
      reload();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    }
  };

  const handleTogglePerk = async (accountId: number, enable: boolean) => {
    setError("");
    try {
      await api.togglePerk(accountId, enable);
      setMessage(`Auto-perk ${enable ? "enabled" : "disabled"}`);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    }
  };

  if (loading) return <section><p>Loading accounts…</p></section>;

  return (
    <section>
      <h2>Accounts</h2>

      {error && <div className="card" style={{ color: "#f87171" }}>{error}</div>}
      {message && <div className="card" style={{ color: "#4ade80" }}>{message}</div>}

      {/* Create Account */}
      <article className="card">
        <h3>Add Account (max 2)</h3>
        <div style={{ display: "flex", gap: 8 }}>
          <input
            type="text"
            placeholder="Account alias"
            value={alias}
            onChange={(e) => setAlias(e.target.value)}
            style={{ padding: "6px 10px", borderRadius: 6, border: "1px solid #29314f", background: "#0b1020", color: "#e5e7eb", flex: 1 }}
          />
          <button onClick={handleCreate} style={{ padding: "6px 16px", borderRadius: 6, background: "#3b82f6", color: "#fff", border: "none", cursor: "pointer" }}>
            Create
          </button>
        </div>
      </article>

      {/* Account List */}
      <div className="grid">
        {accounts.map((acc) => {
          const statusColor = acc.session_status === "valid" ? "#4ade80" : "#f87171";
          return (
            <article key={acc.id} className="card">
              <strong>{acc.alias}</strong>
              <p>
                Session: <span style={{ color: statusColor }}>{acc.session_status}</span>
              </p>
              {acc.last_sync_at && (
                <p style={{ fontSize: "0.85em", opacity: 0.7 }}>
                  Last sync: {new Date(acc.last_sync_at).toLocaleString()}
                </p>
              )}
              <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginTop: 8 }}>
                <button
                  onClick={() => handleRunPerk(acc.id)}
                  style={{ padding: "4px 12px", borderRadius: 6, background: "#10b981", color: "#fff", border: "none", cursor: "pointer", fontSize: "0.85em" }}
                >
                  ▶ Run Perk Now
                </button>
                <button
                  onClick={() => handleTogglePerk(acc.id, true)}
                  style={{ padding: "4px 12px", borderRadius: 6, background: "#6366f1", color: "#fff", border: "none", cursor: "pointer", fontSize: "0.85em" }}
                >
                  ✅ Enable Auto
                </button>
                <button
                  onClick={() => handleTogglePerk(acc.id, false)}
                  style={{ padding: "4px 12px", borderRadius: 6, background: "#64748b", color: "#fff", border: "none", cursor: "pointer", fontSize: "0.85em" }}
                >
                  ⏸️ Disable Auto
                </button>
                <button
                  onClick={() => setSelectedId(acc.id)}
                  style={{ padding: "4px 12px", borderRadius: 6, background: "#f59e0b", color: "#000", border: "none", cursor: "pointer", fontSize: "0.85em" }}
                >
                  🔑 Bootstrap
                </button>
              </div>
            </article>
          );
        })}
      </div>

      {/* Bootstrap Session */}
      {selectedId && (
        <article className="card" style={{ marginTop: 12 }}>
          <h3>Bootstrap Session for Account #{selectedId}</h3>
          <p style={{ fontSize: "0.85em", opacity: 0.7 }}>
            Paste the storage_state JSON from Playwright (cookies + localStorage).
          </p>
          <textarea
            rows={6}
            placeholder='{"cookies": [...], "origins": [...]}'
            value={sessionJson}
            onChange={(e) => setSessionJson(e.target.value)}
            style={{ width: "100%", padding: 8, borderRadius: 6, border: "1px solid #29314f", background: "#0b1020", color: "#e5e7eb", fontFamily: "monospace", fontSize: "0.85em" }}
          />
          <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
            <button onClick={handleBootstrap} style={{ padding: "6px 16px", borderRadius: 6, background: "#3b82f6", color: "#fff", border: "none", cursor: "pointer" }}>
              Save Session
            </button>
            <button onClick={() => { setSelectedId(null); setSessionJson(""); }} style={{ padding: "6px 16px", borderRadius: 6, background: "#64748b", color: "#fff", border: "none", cursor: "pointer" }}>
              Cancel
            </button>
          </div>
        </article>
      )}
    </section>
  );
}
