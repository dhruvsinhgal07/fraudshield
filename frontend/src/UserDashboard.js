import { useEffect, useState } from "react";

const API_URL = process.env.REACT_APP_API_URL || "http://127.0.0.1:8000";

function UserDashboard({ token }) {
  const [history, setHistory] = useState([]);

  useEffect(() => {
    fetch(`${API_URL}/history`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then(res => res.json())
      .then(data => setHistory(data));
  }, [token]);

  return (
    <div>
      <h2>Your History</h2>

      <table style={{ width: "100%", color: "white" }}>
        <thead>
          <tr>
            <th>ID</th>
            <th>Message</th>
            <th>Scam</th>
            <th>Risk %</th>
          </tr>
        </thead>
        <tbody>
          {history.map(row => (
            <tr key={row[0]}>
              <td>{row[0]}</td>
              <td>{row[1]}</td>
              <td>{row[2] ? "Yes" : "No"}</td>
              <td>{row[3].toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default UserDashboard;
