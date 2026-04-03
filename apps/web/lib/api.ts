const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://api:8000";
const API_ADMIN_TOKEN = process.env.API_ADMIN_TOKEN ?? "replace-with-token";

export interface DashboardAccount {
  account_id: number;
  alias: string;
  enabled: boolean;
  session_status: string;
  auto_perk_enabled: boolean;
  next_run_at: string | null;
  last_result: string;
  time_remaining_seconds: number | null;
}

export interface DashboardLog {
  id: number;
  created_at: string;
  action: string;
  status: string;
}

export interface DashboardResponse {
  accounts: DashboardAccount[];
  recent_logs: DashboardLog[];
  generated_at: string;
}

export interface AccountResponse {
  id: number;
  alias: string;
  enabled: boolean;
  session_status: string;
  last_sync_at: string | null;
  last_session_check_at: string | null;
}

export interface GenericLog {
  id: number;
  created_at: string;
  action?: string;
  status?: string;
  event?: string;
  level?: string;
  source?: string;
  message?: string;
}

export interface LogsResponse {
  audit: GenericLog[];
  worker: GenericLog[];
  errors: GenericLog[];
}

async function fetchApi<T>(path: string): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    headers: { "x-admin-token": API_ADMIN_TOKEN },
    cache: "no-store"
  });
  if (!res.ok) {
    throw new Error(`${path} failed: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export const getDashboard = () => fetchApi<DashboardResponse>("/dashboard");
export const getLogs = () => fetchApi<LogsResponse>("/logs");
export const getAccounts = () => fetchApi<AccountResponse[]>("/accounts");
