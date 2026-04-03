export default function DashboardPage() {
  return (
    <section>
      <h2>Dashboard</h2>
      <div className="grid">
        <article className="card"><strong>Account A</strong><p>Session: valid · Next perk: 26m</p></article>
        <article className="card"><strong>Account B</strong><p>Session: re-auth required · Scheduler paused</p></article>
      </div>
      <article className="card">
        <h3>Recent job results</h3>
        <ul>
          <li>perk.run account-a success</li>
          <li>perk.run account-b blocked (session invalid)</li>
        </ul>
      </article>
    </section>
  );
}
