/**
 * RR Control Panel – API client helper.
 *
 * Uses NEXT_PUBLIC_API_URL from env (falls back to /api proxy path).
 * The admin token is read from localStorage so we never hardcode secrets.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "/api";

function headers(): HeadersInit {
  const h: Record<string, string> = { "Content-Type": "application/json" };
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("rr_admin_token") ?? "";
    if (token) h["X-Admin-Token"] = token;
  }
  return h;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { ...headers(), ...(init?.headers ?? {}) },
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API ${res.status}: ${body}`);
  }
  return res.json() as Promise<T>;
}

// ── Types ───────────────────────────────────────────────────────────

export interface Account {
  id: number;
  alias: string;
  enabled: boolean;
  session_status: string;
  last_sync_at: string | null;
}

export interface PerkJob {
  id: number;
  account_id: number;
  auto_enabled: boolean;
  next_run_at: string | null;
  last_result: string | null;
  retry_count: number;
}

export interface AuditLogEntry {
  id: number;
  account_id: number | null;
  action: string;
  status: string;
  details: Record<string, unknown>;
  created_at: string | null;
}

export interface WorkerLogEntry {
  id: number;
  level: string;
  event: string;
  payload: Record<string, unknown>;
  created_at: string | null;
}

export interface DashboardData {
  accounts: Account[];
  jobs: PerkJob[];
  recent_logs: AuditLogEntry[];
}

export interface LogsData {
  audit: AuditLogEntry[];
  worker: WorkerLogEntry[];
}

export interface CityTag {
  id: number;
  account_id: number | null;
  city_name: string;
  type: "friend" | "enemy";
  color: string;
  notes: string | null;
}

export interface PerkRunResult {
  success: boolean;
  message: string;
  next_run_at: string | null;
}

// ── API calls ───────────────────────────────────────────────────────

export const api = {
  health: () => request<{ status: string }>("/health"),

  // Dashboard
  dashboard: () => request<DashboardData>("/dashboard"),

  // Accounts
  listAccounts: () => request<Account[]>("/accounts"),
  createAccount: (alias: string) =>
    request<Account>("/accounts", {
      method: "POST",
      body: JSON.stringify({ alias }),
    }),
  bootstrapSession: (accountId: number, sessionJson: string) =>
    request<Account>(`/accounts/${accountId}/bootstrap`, {
      method: "POST",
      body: JSON.stringify({ session_json: sessionJson }),
    }),

  // Perk
  runPerkNow: (accountId: number) =>
    request<PerkRunResult>(`/accounts/${accountId}/perk/run-now`, { method: "POST" }),
  togglePerk: (accountId: number, autoEnabled: boolean) =>
    request<{ account_id: number; auto_enabled: boolean }>(
      `/accounts/${accountId}/perk/toggle`,
      { method: "POST", body: JSON.stringify({ auto_enabled: autoEnabled }) },
    ),

  // Tags
  listTags: () => request<CityTag[]>("/tags"),

  // Wars
  listWars: () =>
    request<{ id: number; title: string; participants: string; status: string; last_update_at: string | null }[]>(
      "/wars",
    ),

  // Logs
  listLogs: (skip = 0, limit = 50, accountId?: number) => {
    const params = new URLSearchParams({ skip: String(skip), limit: String(limit) });
    if (accountId !== undefined) params.set("account_id", String(accountId));
    return request<LogsData>(`/logs?${params}`);
  },
};
