import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';

const CommandCenter: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuthStore();

  const handleNewCase = () => {
    navigate('/investigation');
    setTimeout(() => {
      const createForm = document.querySelector('.bg-gray-800.rounded-xl.p-4');
      if (createForm) {
        createForm.scrollIntoView({ behavior: 'smooth' });
      }
    }, 100);
  };

  const handleRunAnalysis = () => {
    navigate('/analytics');
  };

  const handleGenerateReport = () => {
    navigate('/report');
  };

  const handleSystemSettings = () => {
    alert('⚙️ System Settings - Coming Soon\n\nFitur ini akan segera tersedia.');
  };

  const quickActions = [
    { name: 'New Case', icon: '📋', action: handleNewCase, color: 'bg-blue-500', description: 'Create new investigation case' },
    { name: 'Run Analysis', icon: '🔍', action: handleRunAnalysis, color: 'bg-purple-500', description: 'Run risk analysis' },
    { name: 'Generate Report', icon: '📊', action: handleGenerateReport, color: 'bg-green-500', description: 'Generate intelligence report' },
    { name: 'System Settings', icon: '⚙️', action: handleSystemSettings, color: 'bg-gray-500', description: 'Configure system settings' },
  ];

  const services = [
    { name: 'API Gateway', status: 'healthy', latency: 45 },
    { name: 'Database', status: 'healthy', latency: 12 },
    { name: 'Redis Cache', status: 'healthy', latency: 5 },
    { name: 'Event Store', status: 'healthy', latency: 23 },
    { name: 'Hash Chain Verifier', status: 'healthy', latency: 8 },
  ];

  const users = [
    { username: 'admin', full_name: 'System Administrator', role: 'ADMIN' },
    { username: 'investigator', full_name: 'Lead Investigator', role: 'INVESTIGATOR' },
    { username: 'auditor', full_name: 'Senior Auditor', role: 'AUDITOR' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gray-800/50 rounded-xl p-4 border border-gray-700">
        <h1 className="text-2xl font-bold text-white">Command Center</h1>
        <p className="text-gray-400 text-sm mt-1">Central command and control for intelligence operations</p>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {quickActions.map((action) => (
          <button
            key={action.name}
            onClick={action.action}
            className={`${action.color} hover:opacity-90 rounded-xl p-6 text-center transition-all transform hover:scale-105`}
          >
            <span className="text-4xl">{action.icon}</span>
            <p className="text-white font-bold mt-2">{action.name}</p>
            <p className="text-xs text-white/70 mt-1">{action.description}</p>
          </button>
        ))}
      </div>

      {/* System Health & User Management */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* System Health */}
        <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-700">
            <h2 className="text-lg font-semibold text-white">System Health</h2>
          </div>
          <div className="p-4">
            {/* Quick Stats */}
            <div className="grid grid-cols-3 gap-4 mb-6">
              <div className="bg-gray-700/30 rounded-lg p-3 text-center">
                <p className="text-2xl font-bold text-green-400">98.5%</p>
                <p className="text-xs text-gray-400">Uptime (24h)</p>
              </div>
              <div className="bg-gray-700/30 rounded-lg p-3 text-center">
                <p className="text-2xl font-bold text-white">12</p>
                <p className="text-xs text-gray-400">Active Tasks</p>
              </div>
              <div className="bg-gray-700/30 rounded-lg p-3 text-center">
                <p className="text-2xl font-bold text-yellow-400">3</p>
                <p className="text-xs text-gray-400">Pending Approvals</p>
              </div>
            </div>

            {/* Services List */}
            <div className="space-y-2">
              {services.map((service) => (
                <div key={service.name} className="flex justify-between items-center p-3 bg-gray-700/20 rounded-lg">
                  <div>
                    <p className="font-medium text-white">{service.name}</p>
                    <p className="text-xs text-gray-500">Latency: {service.latency}ms</p>
                  </div>
                  <div className="text-right">
                    <span className="text-sm font-semibold text-green-400">✅ {service.status}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* User Management */}
        <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-700">
            <h2 className="text-lg font-semibold text-white">User Management</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-900">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-400">Username</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-400">Full Name</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-400">Role</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700">
                {users.map((userItem) => (
                  <tr key={userItem.username} className="hover:bg-gray-700/30">
                    <td className="px-4 py-3 text-white">{userItem.username}</td>
                    <td className="px-4 py-3 text-gray-300">{userItem.full_name}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 rounded-full text-xs ${
                        userItem.role === 'ADMIN' ? 'bg-red-500/20 text-red-400' :
                        userItem.role === 'INVESTIGATOR' ? 'bg-blue-500/20 text-blue-400' :
                        'bg-yellow-500/20 text-yellow-400'
                      }`}>
                        {userItem.role}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="px-4 py-3 border-t border-gray-700">
            <button className="text-sm text-blue-400 hover:text-blue-300">+ Add User</button>
          </div>
        </div>
      </div>

      {/* System Logs Preview */}
      <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-700">
          <h2 className="text-lg font-semibold text-white">Recent System Logs</h2>
        </div>
        <div className="p-4 font-mono text-xs space-y-1">
          <div className="text-green-400">[2026-06-10 08:00:15] System started successfully</div>
          <div className="text-gray-400">[2026-06-10 08:00:32] User admin logged in</div>
          <div className="text-gray-400">[2026-06-10 08:01:05] Hash chain verification completed</div>
          <div className="text-yellow-400">[2026-06-10 08:05:22] New case created: Fraud Investigation</div>
          <div className="text-green-400">[2026-06-10 08:10:00] Integrity check passed (100%)</div>
        </div>
      </div>

      {/* User Info Footer */}
      <div className="text-center text-xs text-gray-500">
        Logged in as: {user?.username || 'admin'} ({user?.role || 'ADMIN'})
      </div>
    </div>
  );
};

export default CommandCenter;
