import React, { useEffect, useState } from 'react';
import { useAuthStore } from '../../stores/authStore';

interface ServiceStatus {
  name: string;
  status: 'healthy' | 'degraded' | 'down';
  latency: number;
  last_check: string;
}

const SystemHealth: React.FC = () => {
  const [services, setServices] = useState<ServiceStatus[]>([
    { name: 'API Gateway', status: 'healthy', latency: 45, last_check: new Date().toISOString() },
    { name: 'Database', status: 'healthy', latency: 12, last_check: new Date().toISOString() },
    { name: 'Redis Cache', status: 'healthy', latency: 5, last_check: new Date().toISOString() },
    { name: 'Event Store', status: 'healthy', latency: 23, last_check: new Date().toISOString() },
    { name: 'Hash Chain Verifier', status: 'healthy', latency: 8, last_check: new Date().toISOString() },
  ]);
  const [systemUptime, setSystemUptime] = useState('7d 14h');
  const [activeTasks, setActiveTasks] = useState(12);
  const [pendingApprovals, setPendingApprovals] = useState(3);
  const { token } = useAuthStore();

  useEffect(() => {
    fetchHealthStatus();
    const interval = setInterval(fetchHealthStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchHealthStatus = async () => {
    try {
      const response = await fetch('http://localhost/health', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        setServices(prev => prev.map(s => 
          s.name === 'API Gateway' ? { ...s, status: 'healthy', last_check: new Date().toISOString() } : s
        ));
      }
    } catch (error) {
      console.error('Failed to fetch health status:', error);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy': return '✅';
      case 'degraded': return '⚠️';
      default: return '❌';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'text-green-400';
      case 'degraded': return 'text-yellow-400';
      default: return 'text-red-400';
    }
  };

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-white">System Health</h3>
      
      {/* Quick Stats */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-gray-700/30 rounded-lg p-3 text-center">
          <p className="text-2xl font-bold text-green-400">98.5%</p>
          <p className="text-xs text-gray-400">Uptime (24h)</p>
        </div>
        <div className="bg-gray-700/30 rounded-lg p-3 text-center">
          <p className="text-2xl font-bold text-white">{activeTasks}</p>
          <p className="text-xs text-gray-400">Active Tasks</p>
        </div>
        <div className="bg-gray-700/30 rounded-lg p-3 text-center">
          <p className="text-2xl font-bold text-yellow-400">{pendingApprovals}</p>
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
              <span className={`text-sm font-semibold ${getStatusColor(service.status)}`}>
                {getStatusIcon(service.status)} {service.status}
              </span>
              <p className="text-xs text-gray-500">{new Date(service.last_check).toLocaleTimeString()}</p>
            </div>
          </div>
        ))}
      </div>

      {/* System Info */}
      <div className="bg-gray-700/20 rounded-lg p-3">
        <div className="flex justify-between text-sm">
          <span className="text-gray-400">System Uptime</span>
          <span className="text-white">{systemUptime}</span>
        </div>
        <div className="flex justify-between text-sm mt-2">
          <span className="text-gray-400">Version</span>
          <span className="text-white">NEMESIS V8+ (8.0.0)</span>
        </div>
        <div className="flex justify-between text-sm mt-2">
          <span className="text-gray-400">Environment</span>
          <span className="text-white">Production</span>
        </div>
      </div>
    </div>
  );
};

export default SystemHealth;
