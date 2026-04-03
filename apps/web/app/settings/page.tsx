"use client";

import { useEffect, useState } from "react";

export default function SettingsPage() {
  const [token, setToken] = useState("");
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem("rr_admin_token") ?? "";
    setToken(stored);
  }, []);

  const save = () => {
    localStorage.setItem("rr_admin_token", token);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const clear = () => {
    localStorage.removeItem("rr_admin_token");
    setToken("");
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <section>
      <h2>Settings</h2>

      <article className="card">
        <h3>🔑 API Admin Token</h3>
        <p style={{ fontSize: "0.85em", opacity: 0.7, marginBottom: 8 }}>
          Set your API admin token. This is stored in localStorage and sent as X-Admin-Token header.
        </p>
        <div style={{ display: "flex", gap: 8 }}>
          <input
            type="password"
            placeholder="Enter admin token"
            value={token}
            onChange={(e) => setToken(e.target.value)}
            style={{ padding: "6px 10px", borderRadius: 6, border: "1px solid #29314f", background: "#0b1020", color: "#e5e7eb", flex: 1, fontFamily: "monospace" }}
          />
          <button onClick={save} style={{ padding: "6px 16px", borderRadius: 6, background: "#3b82f6", color: "#fff", border: "none", cursor: "pointer" }}>
            Save
          </button>
          <button onClick={clear} style={{ padding: "6px 16px", borderRadius: 6, background: "#64748b", color: "#fff", border: "none", cursor: "pointer" }}>
            Clear
          </button>
        </div>
        {saved && <p style={{ color: "#4ade80", marginTop: 8 }}>✅ Saved!</p>}
      </article>

      <article className="card">
        <h3>ℹ️ About</h3>
        <ul style={{ fontSize: "0.9em", lineHeight: 1.8 }}>
          <li>Max accounts: 2</li>
          <li>Perk interval: every 30 minutes</li>
          <li>Worker poll: every 5 minutes</li>
          <li>Encryption: Fernet (AES-128-CBC)</li>
        </ul>
      </article>
    </section>
  );
}
