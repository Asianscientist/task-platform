import { FormEvent, useEffect, useState } from "react";
import { createTask, deleteTask, getQueue, getTasks, getWorkers, login, register, Task } from "./api";

function App() {
  const [token, setToken] = useState(localStorage.getItem("token") ?? "");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [authMode, setAuthMode] = useState<"login" | "register">("login");
  const [tasks, setTasks] = useState<Task[]>([]);
  const [workerCount, setWorkerCount] = useState(0);
  const [queueLength, setQueueLength] = useState(0);
  const [type, setType] = useState("sleep");
  const [seconds, setSeconds] = useState("3");
  const [message, setMessage] = useState("hello");
  const [error, setError] = useState("");

  async function refresh() {
    if (!token) return;
    try {
      const [newTasks, workers, queue] = await Promise.all([
        getTasks(token),
        getWorkers(token),
        getQueue(token),
      ]);
      setTasks(newTasks);
      setWorkerCount(workers.length);
      setQueueLength(queue.length);
      setError("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not refresh");
    }
  }

  useEffect(() => {
    refresh();
    const timer = window.setInterval(refresh, 1000);
    return () => window.clearInterval(timer);
  }, [token]);

  async function handleAuth(event: FormEvent) {
    event.preventDefault();
    setError("");
    try {
      if (authMode === "register") await register(email, password);
      const result = await login(email, password);
      localStorage.setItem("token", result.access_token);
      setToken(result.access_token);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Authentication failed");
    }
  }

  async function handleCreate(event: FormEvent) {
    event.preventDefault();
    setError("");
    try {
      const payload =
        type === "sleep"
          ? { seconds: Number(seconds) }
          : { message };
      await createTask(token, type, payload);
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create task");
    }
  }

  async function removeTask(id: string) {
    try {
      await deleteTask(token, id);
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not delete task");
    }
  }

  if (!token) {
    return (
      <main className="center">
        <section className="card auth">
          <h1>Task Platform</h1>
          <p className="muted">Real-time task processing demo</p>
          <form onSubmit={handleAuth}>
            <label>Email<input type="email" value={email} onChange={e => setEmail(e.target.value)} required /></label>
            <label>Password<input type="password" value={password} onChange={e => setPassword(e.target.value)} minLength={8} required /></label>
            <button type="submit">{authMode === "login" ? "Sign in" : "Create account"}</button>
          </form>
          <button className="link" onClick={() => setAuthMode(authMode === "login" ? "register" : "login")}>
            {authMode === "login" ? "Need an account?" : "Already have an account?"}
          </button>
          {error && <p className="error">{error}</p>}
        </section>
      </main>
    );
  }

  return (
    <main className="shell">
      <header>
        <div>
          <h1>Task Platform</h1>
          <p className="muted">Redis-backed job processing dashboard</p>
        </div>
        <button className="secondary" onClick={() => {
          localStorage.removeItem("token");
          setToken("");
        }}>Sign out</button>
      </header>

      <section className="stats">
        <div className="card"><span>Workers</span><strong>{workerCount}</strong></div>
        <div className="card"><span>Queue</span><strong>{queueLength}</strong></div>
        <div className="card"><span>Tasks</span><strong>{tasks.length}</strong></div>
        <div className="card"><span>Completed</span><strong>{tasks.filter(t => t.status === "COMPLETED").length}</strong></div>
      </section>

      <section className="card">
        <h2>Create task</h2>
        <form className="task-form" onSubmit={handleCreate}>
          <label>Type
            <select value={type} onChange={e => setType(e.target.value)}>
              <option value="sleep">sleep</option>
              <option value="echo">echo</option>
            </select>
          </label>
          {type === "sleep" ? (
            <label>Seconds<input type="number" min="0" max="60" value={seconds} onChange={e => setSeconds(e.target.value)} /></label>
          ) : (
            <label>Message<input value={message} onChange={e => setMessage(e.target.value)} /></label>
          )}
          <button type="submit">Queue task</button>
        </form>
      </section>

      <section className="card">
        <div className="section-title">
          <h2>Tasks</h2>
          <button className="secondary" onClick={refresh}>Refresh</button>
        </div>
        {error && <p className="error">{error}</p>}
        <div className="table-wrap">
          <table>
            <thead><tr><th>ID</th><th>Type</th><th>Status</th><th>Created</th><th>Result / Error</th><th></th></tr></thead>
            <tbody>
              {tasks.map(task => (
                <tr key={task.id}>
                  <td className="mono">{task.id.slice(0, 8)}…</td>
                  <td>{task.type}</td>
                  <td><span className={`status ${task.status.toLowerCase()}`}>{task.status}</span></td>
                  <td>{new Date(task.created_at).toLocaleTimeString()}</td>
                  <td>{task.error ?? task.result ?? "—"}</td>
                  <td>{task.status !== "RUNNING" && <button className="danger" onClick={() => removeTask(task.id)}>Delete</button>}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {tasks.length === 0 && <p className="muted empty">No tasks yet.</p>}
      </section>
    </main>
  );
}

export default App;
