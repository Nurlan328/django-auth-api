// Tiny API client. The base URL points at either backend (FastAPI or Django),
// since both expose the same REST API. Set it in .env via VITE_API_BASE.
const BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

export const getToken = () => localStorage.getItem("token");
export const setToken = (t) => localStorage.setItem("token", t);
export const clearToken = () => localStorage.removeItem("token");

function authHeaders() {
  const t = getToken();
  return t ? { Authorization: `Bearer ${t}` } : {};
}

function extractError(data, status) {
  if (!data) return `Error ${status}`;
  if (data.detail) return data.detail;            // FastAPI / DRF generic errors
  if (typeof data === "object") {
    const first = Object.values(data).flat()[0];  // DRF field errors: {username: [...]}
    if (first) return String(first);
  }
  return `Error ${status}`;
}

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...authHeaders(), ...(options.headers || {}) },
  });
  const data = res.status === 204 ? null : await res.json().catch(() => null);
  if (!res.ok) throw new Error(extractError(data, res.status));
  return data;
}

export const api = {
  register: (body) =>
    request("/auth/register", { method: "POST", body: JSON.stringify(body) }),

  // Login is sent as form-encoded: FastAPI's OAuth2 form requires it, and DRF
  // accepts it too. The token field name differs between the two backends.
  login: async (username, password) => {
    const res = await fetch(`${BASE}/auth/login`, {
      method: "POST",
      body: new URLSearchParams({ username, password }),
    });
    const data = await res.json().catch(() => null);
    if (!res.ok) throw new Error(extractError(data, res.status));
    const token = data.access_token || data.access; // FastAPI: access_token, Django: access
    setToken(token);
    return token;
  },

  me: () => request("/users/me"),
  users: () => request("/admin/users"),
  stats: () => request("/admin/stats"),
};
