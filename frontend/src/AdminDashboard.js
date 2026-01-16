import { useEffect, useState } from "react";
import { Bar, Pie } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Tooltip,
  Legend
} from "chart.js";

const API_URL = process.env.REACT_APP_API_URL || "http://127.0.0.1:8000";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Tooltip,
  Legend
);

function AdminDashboard({ token }) {
  const [analytics, setAnalytics] = useState(null);

  useEffect(() => {
    fetch(`${API_URL}/analytics`, {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(setAnalytics);
  }, [token]);

  if (!analytics) return <p>Loading analytics...</p>;

  const pieData = {
    labels: ["Scam", "Safe"],
    datasets: [
      {
        data: [analytics.scam, analytics.safe],
        backgroundColor: ["#ff4d4f", "#2ecc71"],
        borderWidth: 0
      }
    ]
  };

  const barData = {
    labels: analytics.daily.map(d => d[0]),
    datasets: [
      {
        label: "Reports",
        data: analytics.daily.map(d => d[1]),
        backgroundColor: "#4f9cff",
        borderRadius: 8
      }
    ]
  };

  return (
    <div style={{ marginTop: "50px" }}>
      <h2>Admin Analytics Dashboard 📊</h2>

      <div
        style={{
          display: "flex",
          justifyContent: "center",
          gap: "30px",
          marginTop: "30px"
        }}
      >
        <StatCard title="Total Reports" value={analytics.total} />
        <StatCard title="Scams" value={analytics.scam} color="#ff4d4f" />
        <StatCard title="Safe" value={analytics.safe} color="#2ecc71" />
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "40px",
          marginTop: "50px"
        }}
      >
        <GlassCard>
          <h3>Scam vs Safe</h3>
          <Pie data={pieData} />
        </GlassCard>

        <GlassCard>
          <h3>Reports per Day</h3>
          <Bar data={barData} />
        </GlassCard>
      </div>
    </div>
  );
}

function StatCard({ title, value, color = "#4f9cff" }) {
  return (
    <div
      style={{
        background: "rgba(255,255,255,0.07)",
        padding: "20px 30px",
        borderRadius: "15px",
        minWidth: "160px",
        textAlign: "center",
        boxShadow: "0 10px 30px rgba(0,0,0,0.4)"
      }}
    >
      <p style={{ opacity: 0.8 }}>{title}</p>
      <h2 style={{ color }}>{value}</h2>
    </div>
  );
}

function GlassCard({ children }) {
  return (
    <div
      style={{
        background: "rgba(255,255,255,0.06)",
        borderRadius: "18px",
        padding: "25px",
        boxShadow: "0 15px 40px rgba(0,0,0,0.5)"
      }}
    >
      {children}
    </div>
  );
}

export default AdminDashboard;
