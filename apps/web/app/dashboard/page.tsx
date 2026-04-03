import { DashboardAccount, DashboardLog, getDashboard } from "../../lib/api";

export default async function DashboardPage() {
  try {
    const data = await getDashboard();
    return (
      <section>
        <h2>Dashboard</h2>
        <div className="grid">
          {data.accounts.map((account: DashboardAccount) => (
            <article className="card" key={account.account_id}>
              <strong>{account.alias}</strong>
              <p>Session: {account.session_status}</p>
              <p>Enabled: {String(account.enabled)}</p>
              <p>Auto Perk: {account.auto_perk_enabled ? "enabled" : "disabled"}</p>
              <p>Last Result: {account.last_result}</p>
              <p>Next Run: {account.next_run_at ?? "-"}</p>
              <p>Remaining (s): {account.time_remaining_seconds ?? "-"}</p>
            </article>
          ))}
        </div>
        <article className="card">
          <h3>Recent audit logs</h3>
          <ul>
            {data.recent_logs.map((log: DashboardLog) => (
              <li key={log.id}>
                {log.created_at} · {log.action} · {log.status}
              </li>
            ))}
          </ul>
        </article>
      </section>
    );
  } catch (error) {
    return <div className="card">Dashboard yüklenemedi: {(error as Error).message}</div>;
  }
}
