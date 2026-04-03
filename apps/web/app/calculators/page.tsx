export default function CalculatorsPage() {
  return (
    <section>
      <h2>Calculators</h2>
      <div className="grid">
        <article className="card"><h3>Perk</h3><p>Estimate perk cycle and next action.</p></article>
        <article className="card"><h3>Region Cost</h3><p>Calculate costs by level and modifiers.</p></article>
        <article className="card"><h3>Production</h3><p>Estimate production totals and deltas.</p></article>
        <article className="card"><h3>Mercenary</h3><p>Compute expected hiring budget.</p></article>
      </div>
    </section>
  );
}
