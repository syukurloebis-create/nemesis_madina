import React, { useState, useEffect } from 'react';
import { useAuthStore } from '../../stores/authStore';

interface User {
  id: string;
  username: string;
  email: string;
  full_name: string;
  role: string;
  institution_id: string;
  is_active: boolean;
  created_at: string;
}

const UserManagement: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newUser, setNewUser] = useState({ username: '', email: '', password: '', full_name: '', role: 'VIEWER' });
  const { token } = useAuthStore();

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost/admin/users', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setUsers(data.data || []);
      } else {
        // Mock data
        setUsers([
          { id: '1', username: 'admin', email: 'admin@nemesis.com', full_name: 'System Administrator', role: 'ADMIN', institution_id: 'inspektorat-1', is_active: true, created_at: new Date().toISOString() },
          { id: '2', username: 'investigator', email: 'investigator@nemesis.com', full_name: 'Lead Investigator', role: 'INVESTIGATOR', institution_id: 'kpk-1', is_active: true, created_at: new Date().toISOString() },
          { id: '3', username: 'auditor', email: 'auditor@nemesis.com', full_name: 'Senior Auditor', role: 'AUDITOR', institution_id: 'inspektorat-1', is_active: true, created_at: new Date().toISOString() },
        ]);
      }
    } catch (error) {
      console.error('Failed to fetch users:', error);
    } finally {
      setLoading(false);
    }
  };

  const addUser = async () => {
    if (!newUser.username || !newUser.email || !newUser.password) return;
    try {
      const response = await fetch('http://localhost/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(newUser)
      });
      if (response.ok) {
        const data = await response.json();
        setUsers([...users, data.user || data]);
        setShowAddForm(false);
        setNewUser({ username: '', email: '', password: '', full_name: '', role: 'VIEWER' });
      }
    } catch (error) {
      console.error('Failed to add user:', error);
    }
  };

  const toggleUserStatus = async (userId: string, currentStatus: boolean) => {
    try {
      await fetch(`http://localhost/admin/users/${userId}/toggle`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setUsers(users.map(u => u.id === userId ? { ...u, is_active: !currentStatus } : u));
    } catch (error) {
      console.error('Failed to toggle user status:', error);
    }
  };

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'ADMIN': return 'bg-red-500/20 text-red-400';
      case 'INVESTIGATOR': return 'bg-blue-500/20 text-blue-400';
      case 'AUDITOR': return 'bg-yellow-500/20 text-yellow-400';
      case 'PROSECUTOR': return 'bg-purple-500/20 text-purple-400';
      default: return 'bg-gray-500/20 text-gray-400';
    }
  };

  if (loading) {
    return <div className="text-center py-8 text-gray-400">Loading users...</div>;
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold text-white">User Management</h3>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="px-3 py-1 text-sm bg-green-500/20 text-green-400 rounded-lg hover:bg-green-500/30"
        >
          + Add User
        </button>
      </div>

      {showAddForm && (
        <div className="bg-gray-700/30 rounded-lg p-4 space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <input
              type="text"
              placeholder="Username"
              value={newUser.username}
              onChange={(e) => setNewUser({ ...newUser, username: e.target.value })}
              className="px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
            />
            <input
              type="email"
              placeholder="Email"
              value={newUser.email}
              onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
              className="px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
            />
            <input
              type="password"
              placeholder="Password"
              value={newUser.password}
              onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
              className="px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
            />
            <input
              type="text"
              placeholder="Full Name"
              value={newUser.full_name}
              onChange={(e) => setNewUser({ ...newUser, full_name: e.target.value })}
              className="px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
            />
            <select
              value={newUser.role}
              onChange={(e) => setNewUser({ ...newUser, role: e.target.value })}
              className="px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
            >
              <option value="VIEWER">Viewer</option>
              <option value="AUDITOR">Auditor</option>
              <option value="INVESTIGATOR">Investigator</option>
              <option value="PROSECUTOR">Prosecutor</option>
              <option value="ADMIN">Admin</option>
            </select>
          </div>
          <div className="flex gap-2">
            <button onClick={addUser} className="px-4 py-2 bg-green-500 text-white rounded-lg">Save</button>
            <button onClick={() => setShowAddForm(false)} className="px-4 py-2 bg-gray-600 text-white rounded-lg">Cancel</button>
          </div>
        </div>
      )}

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-700/50">
            <tr>
              <th className="px-4 py-3 text-left text-xs text-gray-400">Username</th>
              <th className="px-4 py-3 text-left text-xs text-gray-400">Full Name</th>
              <th className="px-4 py-3 text-left text-xs text-gray-400">Role</th>
              <th className="px-4 py-3 text-left text-xs text-gray-400">Status</th>
              <th className="px-4 py-3 text-left text-xs text-gray-400">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-700">
            {users.map((user) => (
              <tr key={user.id} className="hover:bg-gray-700/30">
                <td className="px-4 py-3 text-white">{user.username}</td>
                <td className="px-4 py-3 text-gray-300">{user.full_name}</td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-1 rounded-full text-xs ${getRoleColor(user.role)}`}>
                    {user.role}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-1 rounded-full text-xs ${user.is_active ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                    {user.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <button
                    onClick={() => toggleUserStatus(user.id, user.is_active)}
                    className="text-xs text-blue-400 hover:text-blue-300"
                  >
                    {user.is_active ? 'Deactivate' : 'Activate'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default UserManagement;
