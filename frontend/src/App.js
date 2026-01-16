import { useState } from "react";
import "./App.css";
import { jwtDecode } from "jwt-decode";

import AdminDashboard from "./AdminDashboard";
import UserDashboard from "./UserDashboard";
import AdminUsers from "./AdminUsers";

const API_URL = process.env.REACT_APP_API_URL || "http://127.0.0.1:8000";

function App() {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const [token, setToken] = useState(localStorage.getItem("token"));
  const [isLogin, setIsLogin] = useState(true);

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const userRole = token ? jwtDecode(token).role : null;

  /* ================= AUTH ================= */

  const login = async () => {
    try {
      const res = await fetch(`${API_URL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();
      if (data.token) {
        localStorage.setItem("token", data.token);
        setToken(data.token);
      } else {
        alert(data.error || "Login failed");
      }
    } catch (err) {
      alert("Backend not reachable");
    }
  };

  const signup = async () => {
    const res = await fetch(`${API_URL}/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, email, password }),
    });

    const data = await res.json();
    alert(data.message || data.error);
  };

  const logout = () => {
    localStorage.removeItem("token");
    setToken(null);
  };

  /* ================= SCAM CHECK ================= */

  const checkScam = async () => {
    setLoading(true);
    setResult(null);

    try {
      const res = await fetch(`${API_URL}/predict`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ text }),
      });

      const data = await res.json();
      setResult(data);
    } catch {
      alert("Prediction failed");
    }

    setLoading(false);
  };

  /* ================= LOGIN / SIGNUP UI ================= */

  if (!token) {
    return (
      <div className="app auth-page">
        <div className="auth-card">
          <h1>{isLogin ? "Welcome Back" : "Create Account"}</h1>

          {!isLogin && (
            <input
              placeholder="Full Name"
              onChange={(e) => setName(e.target.value)}
            />
          )}

          <input
            placeholder="Email"
            onChange={(e) => setEmail(e.target.value)}
          />

          <input
            type="password"
            placeholder="Password"
            onChange={(e) => setPassword(e.target.value)}
          />

          <button onClick={isLogin ? login : signup}>
            {isLogin ? "Login" : "Sign Up"}
          </button>

          <p
            className="auth-switch"
            onClick={() => setIsLogin(!isLogin)}
          >
            {isLogin
              ? "Don’t have an account? Sign up"
              : "Already have an account? Login"}
          </p>
        </div>
      </div>
    );
  }

  /* ================= LOGGED IN UI ================= */
  
  return (
    <div className="app dashboard">
      {/* Logout */}
      <button className="logout-btn" onClick={logout}>
        Logout
      </button>

      <h1 className="title">FraudShield 🛡️</h1>

      {/* Input */}
      <textarea
        placeholder="Paste SMS, email, or message here..."
        value={text}
        onChange={(e) => setText(e.target.value)}
      />

      <button className="primary-btn" onClick={checkScam}>
        Check Message
      </button>

      {loading && <p className="loading">Analyzing...</p>}

      {/* Result */}
      {result && (
        <div className="result-card">
          {(() => {
            let status = "Looks Safe";
            let color = "#2ecc71";

            if (result.scam) {
              status = "🚨 Scam Detected";
              color = "#ff4d4f";
            } else if (result.confidence > 30) {
              status = "⚠️ Suspicious";
              color = "#faad14";
            }

            return <h2 style={{ color }}>{status}</h2>;
          })()}

          <p>Scam Risk: {result.confidence}%</p>

          {result.urls_detected?.length > 0 && (
            <div className="url-box">
              <strong>🔗 URLs detected:</strong>
              <ul>
                {result.urls_detected.map((url, i) => (
                  <li key={i}>{url}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Role Based Dashboard */}
      <div className="dashboard-section">
        {userRole === "admin" ? (
          <>
            <AdminDashboard token={token} />
            <AdminUsers token={token} />
          </>
        ) : (
          <UserDashboard token={token} />
        )}
      </div>
    </div>
  );
}

export default App;
