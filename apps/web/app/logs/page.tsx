import { GenericLog, getLogs } from "../../lib/api";

export default async function LogsPage() {
  try {
    const logs = await getLogs();
    return (
      <section>
        <h2>Logs</h2>
        <article className="card">
          <h3>Audit</h3>
          <ul>
            {logs.audit.map((l: GenericLog) => (
              <li key={`a-${l.id}`}>{l.created_at} · {l.action} · {l.status}</li>
            ))}
          </ul>
        </article>
        <article className="card">
          <h3>Worker</h3>
          <ul>
            {logs.worker.map((l: GenericLog) => (
              <li key={`w-${l.id}`}>{l.created_at} · {l.event} · {l.level}</li>
            ))}
          </ul>
        </article>
        <article className="card">
          <h3>Error</h3>
          <ul>
            {logs.errors.map((l: GenericLog) => (
              <li key={`e-${l.id}`}>{l.created_at} · {l.source} · {l.message}</li>
            ))}
          </ul>
        </article>
      </section>
    );
  } catch (error) {
    return <div className="card">Logs yüklenemedi: {(error as Error).message}</div>;
  }
}
