import React, { useEffect, useState } from 'react';
import { useAuthStore } from '../../stores/authStore';

interface ServiceStatus {
  name: string;
  status: 'healthy' | 'degraded' | 'down';
  latency: number;
  last_check: string;
  endpoint: string;
}

const SystemStatus: React.FC = () => {
  const [services, setServices] = useState<ServiceStatus[]>([
    { name: 'API Gateway', status: 'healthy', latency: 0, last_check: '', endpoint: '/health' },
    { name: 'Database', status: 'healthy', latency: 0, last_check: '', endpoint: '/health/db' },
    { name: 'Redis Cache', status: 'healthy', latency: 0, last_check: '', endpoint: '/health/redis' },
    { name: 'Event Store', status: 'healthy', latency: 0, last_check: '', endpoint: '/health/events' },
    { name: 'Hash Chain Verifier', status: 'healthy', latency: 0, last_check: '', endpoint: '/health/hash' },
    { name: 'Prometheus', status: 'healthy', latency: 0, last_check: '', endpoint: 'http://localhost:9090/-/healthy' },
    { name: 'Grafana', status: 'healthy', latency: 0, last_check: '', endpoint: 'http://localhost:3000/api/health' },
  ]);
  const [overallStatus, setOverallStatus] = useState<'healthy' | 'degraded' | 'down'>('healthy');
  const [refreshing, setRefreshing] = useState(false);
  const { token } = useAuthStore();

  const checkService = async (service: ServiceStatus) => {
    const start = performance.now();
    try {
      const response = await fetch(service.endpoint.startsWith('http') ? service.endpoint : `http://localhost${service.endpoint}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const latency = Math.round(performance.now() - start);
      return {
        ...service,
        status: response.ok ? 'healthy' : 'degraded',
        latency,
        last_check: new Date().toISOString()
      };
    } catch (error) {
      return {
        ...service,
        status: 'down' as const,
        latency: 0,
        last_check: new Date().toISOString()
      };
    }
  };

  const refreshStatus = async () => {
    setRefreshing(true);
    const updatedServices = await Promise.all(services.map(checkService));
    setServices(updatedServices);
    
    const hasDown = updatedServices.some(s => s.status === 'down');
    const hasDegraded = updatedServices.some(s => s.status === 'degraded');
    
    if (hasDown) setOverallStatus('down');
    else if (hasDegraded) setOverallStatus('degraded');
    else setOverallStatus('healthy');
    
    setRefreshing(false);
  };

  useEffect(() => {
    refreshStatus();
    const interval = setInterval(refreshStatus, 60000);
    return () => clearInterval(interval);
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy': return '🟢';
      case 'degraded': return '🟡';
      default: return '🔴';
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
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-2">
          <h3 className="text-lg font-semibold text-white">System Status</h3>
          <div className={`px-2 py-1 rounded-full text-xs ${getStatusColor(overallStatus)} bg-gray-700`}>
            {getStatusIcon(overallStatus)} {overallStatus.toUpperCase()}
          </div>
        </div>
        <button
          onClick={refreshStatus}
          disabled={refreshing}
          className="px-3 py-1 text-sm bg-gray-700 rounded-lg hover:bg-gray-600 disabled:opacity-50"
        >
          {refreshing ? '⟳' : '↻'} Refresh
        </button>
      </div>

      <div className="grid gap-3">
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
              <p className="text-xs text-gray-500">{service.last_check ? new Date(service.last_check).toLocaleTimeString() : '-'}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SystemStatus;
