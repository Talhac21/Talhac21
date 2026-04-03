"use client";

import { useEffect, useState } from "react";
import { api, type CityTag } from "../lib/api";

export default function TagsPage() {
  const [tags, setTags] = useState<CityTag[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .listTags()
      .then(setTags)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <section><p>Loading tags…</p></section>;
  if (error) return <section><div className="card" style={{ color: "#f87171" }}>Error: {error}</div></section>;

  const friends = tags.filter((t) => t.type === "friend");
  const enemies = tags.filter((t) => t.type === "enemy");

  return (
    <section>
      <h2>Friend / Enemy City Tags</h2>

      {tags.length === 0 && (
        <div className="card"><p>No city tags yet. Tags will appear when added via the API.</p></div>
      )}

      {friends.length > 0 && (
        <>
          <h3 style={{ color: "#4ade80" }}>🤝 Friends</h3>
          <div className="grid">
            {friends.map((t) => (
              <article key={t.id} className="card">
                <strong style={{ color: t.color }}>{t.city_name}</strong>
                {t.notes && <p style={{ fontSize: "0.85em", opacity: 0.7 }}>{t.notes}</p>}
              </article>
            ))}
          </div>
        </>
      )}

      {enemies.length > 0 && (
        <>
          <h3 style={{ color: "#f87171" }}>⚔️ Enemies</h3>
          <div className="grid">
            {enemies.map((t) => (
              <article key={t.id} className="card">
                <strong style={{ color: t.color }}>{t.city_name}</strong>
                {t.notes && <p style={{ fontSize: "0.85em", opacity: 0.7 }}>{t.notes}</p>}
              </article>
            ))}
          </div>
        </>
      )}
    </section>
  );
}
