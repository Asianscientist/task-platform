const API_URL = import.meta.env.VITE_API_URL ?? "";

export type Task = {
  id: string;
  type: string;
  payload: Record<string, unknown>;
  status: string;
  result: string | null;
  error: string | null;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
};

async function request(path: string, options: RequestInit = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers ?? {}),
    },
  });

  if (!response.ok) {
    let detail = "Request failed";
    try {
      const body = await response.json();
      detail = body.detail ?? detail;
    } catch {}
    throw new Error(detail);
  }

  if (response.status === 204) return null;
  return response.json();
}

export async function register(email: string, password: string) {
  return request("/api/auth/register", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export async function login(email: string, password: string) {
  return request("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export async function getTasks(token: string): Promise<Task[]> {
  return request("/api/tasks", {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export async function createTask(
  token: string,
  type: string,
  payload: Record<string, unknown>
): Promise<Task> {
  return request("/api/tasks", {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify({ type, payload }),
  });
}

export async function deleteTask(token: string, id: string) {
  return request(`/api/tasks/${id}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  });
}

export async function getWorkers(token: string) {
  return request("/api/workers", {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export async function getQueue(token: string) {
  return request("/api/workers/queue", {
    headers: { Authorization: `Bearer ${token}` },
  });
}
