import { useState } from "react";
import { api } from "../api";

export default function AuthForm({ onLoggedIn }) {
  const [mode, setMode] = useState("login"); // "login" | "register"
  const [form, setForm] = useState({ username: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const update = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  async function submit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      if (mode === "register") {
        await api.register(form);
      }
      // Log in (also right after a successful registration).
      await api.login(form.username, form.password);
      onLoggedIn();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="card">
      <div className="tabs">
        <button className={mode === "login" ? "active" : ""} onClick={() => setMode("login")}>
          Login
        </button>
        <button className={mode === "register" ? "active" : ""} onClick={() => setMode("register")}>
          Register
        </button>
      </div>

      <form onSubmit={submit}>
        <input name="username" placeholder="username" value={form.username} onChange={update} required />
        {mode === "register" && (
          <input name="email" type="email" placeholder="email" value={form.email} onChange={update} required />
        )}
        <input
          name="password"
          type="password"
          placeholder="password"
          value={form.password}
          onChange={update}
          required
        />
        <button type="submit" disabled={busy}>
          {busy ? "…" : mode === "login" ? "Log in" : "Sign up"}
        </button>
      </form>

      {error && <p className="error">{error}</p>}
    </div>
  );
}
