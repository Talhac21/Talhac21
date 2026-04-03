import { AccountResponse, getAccounts } from "../../lib/api";

export default async function AccountsPage() {
  try {
    const accounts = await getAccounts();
    return (
      <section>
        <h2>Accounts</h2>
        <div className="card">
          <p>v1 sınırı: en fazla 2 hesap.</p>
        </div>
        {accounts.map((acc: AccountResponse) => (
          <article className="card" key={acc.id}>
            <strong>{acc.alias}</strong>
            <p>Enabled: {String(acc.enabled)}</p>
            <p>Session: {acc.session_status}</p>
            <p>Last Sync: {acc.last_sync_at ?? "-"}</p>
            <p>Last Session Check: {acc.last_session_check_at ?? "-"}</p>
          </article>
        ))}
      </section>
    );
  } catch (error) {
    return <div className="card">Accounts yüklenemedi: {(error as Error).message}</div>;
  }
}
