import { useEffect, useState } from "react";
import { api } from "../api";

export default function Dashboard({ user, onLogout }) {
  return (
    <div className="card">
      <div className="row">
        <h2>Hello, {user.username}</h2>
        <button className="ghost" onClick={onLogout}>
          Log out
        </button>
      </div>

      <ul className="profile">
        <li><span>ID</span><b>{user.id}</b></li>
        <li><span>Email</span><b>{user.email}</b></li>
        <li><span>Role</span><b className={`role role-${user.role}`}>{user.role}</b></li>
        <li><span>Joined</span><b>{new Date(user.created_at).toLocaleString()}</b></li>
      </ul>

      {user.role === "admin" ? (
        <AdminPanel />
      ) : (
        <p className="hint">Admin tools appear here for users with the admin role.</p>
      )}
    </div>
  );
}

function AdminPanel() {
  const [users, setUsers] = useState([]);
  const [stats, setStats] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.users().then(setUsers).catch((e) => setError(e.message));
  }, []);

  async function loadStats() {
    setError("");
    try {
      setStats(await api.stats());
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <div className="admin">
      <h3>Admin</h3>
      {error && <p className="error">{error}</p>}

      <div className="stats">
        <button onClick={loadStats}>Load stats</button>
        {stats && (
          <span>
            Total users: <b>{stats.total_users}</b> <em>(source: {stats.source})</em>
          </span>
        )}
      </div>

      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Username</th>
            <th>Email</th>
            <th>Role</th>
          </tr>
        </thead>
        <tbody>
          {users.map((u) => (
            <tr key={u.id}>
              <td>{u.id}</td>
              <td>{u.username}</td>
              <td>{u.email}</td>
              <td>{u.role}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
