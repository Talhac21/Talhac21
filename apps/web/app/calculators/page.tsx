"use client";

import { useState } from "react";

export default function CalculatorsPage() {
  const [perkLevel, setPerkLevel] = useState(0);
  const [regionLevel, setRegionLevel] = useState(1);

  // Perk training cost estimation (simplified formula)
  const perkCost = perkLevel > 0 ? Math.floor(perkLevel * 1.5 * 1000) : 0;

  // Region cost estimation (simplified formula based on game mechanics)
  const regionCost = Math.floor(Math.pow(regionLevel, 2) * 500);

  return (
    <section>
      <h2>Calculators</h2>

      <div className="grid">
        <article className="card">
          <h3>🧠 Perk Cost</h3>
          <p style={{ fontSize: "0.85em", opacity: 0.7, marginBottom: 8 }}>
            Estimate training cost for a perk level.
          </p>
          <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <label>Level:</label>
            <input
              type="number"
              min={0}
              max={500}
              value={perkLevel}
              onChange={(e) => setPerkLevel(Number(e.target.value))}
              style={{ width: 80, padding: "4px 8px", borderRadius: 6, border: "1px solid #29314f", background: "#0b1020", color: "#e5e7eb" }}
            />
          </div>
          <p style={{ marginTop: 8 }}>
            Estimated cost: <strong>${perkCost.toLocaleString()}</strong>
          </p>
        </article>

        <article className="card">
          <h3>🏙️ Region Cost</h3>
          <p style={{ fontSize: "0.85em", opacity: 0.7, marginBottom: 8 }}>
            Estimate region upgrade cost by level.
          </p>
          <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <label>Level:</label>
            <input
              type="number"
              min={1}
              max={100}
              value={regionLevel}
              onChange={(e) => setRegionLevel(Number(e.target.value))}
              style={{ width: 80, padding: "4px 8px", borderRadius: 6, border: "1px solid #29314f", background: "#0b1020", color: "#e5e7eb" }}
            />
          </div>
          <p style={{ marginTop: 8 }}>
            Estimated cost: <strong>${regionCost.toLocaleString()}</strong>
          </p>
        </article>

        <article className="card">
          <h3>⚙️ Production</h3>
          <p style={{ fontSize: "0.85em", opacity: 0.7 }}>
            Production calculators depend on region data from the game. Connect your account to see live estimates.
          </p>
        </article>

        <article className="card">
          <h3>⚔️ Mercenary</h3>
          <p style={{ fontSize: "0.85em", opacity: 0.7 }}>
            Mercenary budget calculators depend on war data. Check the Wars page for live info.
          </p>
        </article>
      </div>
    </section>
  );
}
