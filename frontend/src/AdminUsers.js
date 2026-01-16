import { useEffect, useState } from "react";

const API_URL = process.env.REACT_APP_API_URL || "http://127.0.0.1:8000";

function AdminUsers({ token }) {
  const [users, setUsers] = useState([]);

  const loadUsers = () => {
    fetch(`${API_URL}/admin/users`, {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(setUsers);
  };

 useEffect(() => {
  if (token) {
    loadUsers();
  }
}, [token]);

  const deleteUser = id => {
    if (!window.confirm("Delete this user?")) return;

  fetch(`${API_URL}/admin/users`, {
  headers: {
    Authorization: `Bearer ${token}`
  }
})

.then(loadUsers);
  };

  return (
    <div style={{ marginTop: "40px" }}>
      <h2>User Management 👥</h2>

      <table style={{ width: "100%", marginTop: "20px" }}>
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Email</th>
            <th>Role</th>
            <th>Action</th>
          </tr>
        </thead>

        <tbody>
          {users.map(u => (
            <tr key={u[0]}>
              <td>{u[0]}</td>
              <td>{u[1]}</td>
              <td>{u[2]}</td>
              <td>{u[3]}</td>
              <td>
                <button
                  style={{ background: "red", color: "white" }}
                  onClick={() => deleteUser(u[0])}
                >
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default AdminUsers;
