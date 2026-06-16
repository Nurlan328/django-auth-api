import { useEffect, useState } from "react";
import { api, getToken, clearToken } from "./api";
import AuthForm from "./components/AuthForm";
import Dashboard from "./components/Dashboard";
import "./App.css";

const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

export default function App() {
  const [authed, setAuthed] = useState(!!getToken());
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(!!getToken());

  // When authed, load the current user. A bad/expired token logs us out.
  useEffect(() => {
    if (!authed) {
      setUser(null);
      setLoading(false);
      return;
    }
    setLoading(true);
    api
      .me()
      .then(setUser)
      .catch(() => {
        clearToken();
        setAuthed(false);
      })
      .finally(() => setLoading(false));
  }, [authed]);

  return (
    <div className="app">
      <header>
        <h1>Auth API — demo</h1>
        <span className="api-base">{API_BASE}</span>
      </header>

      {loading ? (
        <div className="card">
          <p className="hint">Loading…</p>
        </div>
      ) : authed && user ? (
        <Dashboard user={user} onLogout={() => { clearToken(); setAuthed(false); }} />
      ) : (
        <AuthForm onLoggedIn={() => setAuthed(true)} />
      )}
    </div>
  );
}
