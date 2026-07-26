/**
 * System Status Component
 * Real-time system health monitoring
 */
import React, { useState, useEffect } from 'react';
import { Activity, CheckCircle, AlertCircle, Clock, Database, Server, Cpu, HardDrive } from 'lucide-react';

interface SystemHealth {
  status: 'healthy' | 'degraded' | 'down';
  uptime: number;
  services: {
    [key: string]: {
      status: 'up' | 'down' | 'degraded';
      latency: number;
      lastCheck: string;
    };
  };
  metrics: {
    cpu: number;
    memory: number;
    disk: number;
    requests: number;
    errors: number;
    responseTime: number;
  };
}

export const SystemStatus: React.FC = () => {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const response = await fetch('/api/v1/health');
        const data = await response.json();
        setHealth(data);
        setError(null);
      } catch (err) {
        setError('Failed to fetch system health');
      } finally {
        setLoading(false);
      }
    };

    fetchHealth();
    const interval = setInterval(fetchHealth, 30000); // Every 30 seconds

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="animate-pulse">
        <div className="h-32 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
      </div>
    );
  }

  if (error || !health) {
    return (
      <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 text-red-600 dark:text-red-400">
        <AlertCircle className="inline-block mr-2" />
        {error || 'System health unavailable'}
      </div>
    );
  }

  const statusColors = {
    healthy: 'text-green-500',
    degraded: 'text-yellow-500',
    down: 'text-red-500'
  };

  const statusIcons = {
    healthy: CheckCircle,
    degraded: AlertCircle,
    down: AlertCircle
  };

  const StatusIcon = statusIcons[health.status];

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
          <Activity className="w-5 h-5" />
          System Status
        </h3>
        <div className="flex items-center gap-2">
          <StatusIcon className={`w-5 h-5 ${statusColors[health.status]}`} />
          <span className={`font-medium ${statusColors[health.status]}`}>
            {health.status.charAt(0).toUpperCase() + health.status.slice(1)}
          </span>
        </div>
      </div>

      {/* Uptime */}
      <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 mb-4">
        <Clock className="w-4 h-4" />
        <span>Uptime: {formatUptime(health.uptime)}</span>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <MetricCard
          icon={<Cpu className="w-4 h-4" />}
          label="CPU"
          value={`${health.metrics.cpu}%`}
          status={health.metrics.cpu > 80 ? 'warning' : health.metrics.cpu > 60 ? 'info' : 'success'}
        />
        <MetricCard
          icon={<Database className="w-4 h-4" />}
          label="Memory"
          value={`${health.metrics.memory}%`}
          status={health.metrics.memory > 80 ? 'warning' : health.metrics.memory > 60 ? 'info' : 'success'}
        />
        <MetricCard
          icon={<HardDrive className="w-4 h-4" />}
          label="Disk"
          value={`${health.metrics.disk}%`}
          status={health.metrics.disk > 80 ? 'warning' : health.metrics.disk > 60 ? 'info' : 'success'}
        />
        <MetricCard
          icon={<Server className="w-4 h-4" />}
          label="Response"
          value={`${health.metrics.responseTime}ms`}
          status={health.metrics.responseTime > 500 ? 'warning' : health.metrics.responseTime > 200 ? 'info' : 'success'}
        />
      </div>

      {/* Services */}
      <div className="space-y-2">
        <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">Services</h4>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
          {Object.entries(health.services).map(([name, service]) => (
            <ServiceStatus
              key={name}
              name={name}
              status={service.status}
              latency={service.latency}
            />
          ))}
        </div>
      </div>

      {/* Request Stats */}
      <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
        <div className="flex justify-between text-sm">
          <span className="text-gray-600 dark:text-gray-400">Requests</span>
          <span className="font-medium">{health.metrics.requests.toLocaleString()}</span>
        </div>
        <div className="flex justify-between text-sm mt-1">
          <span className="text-gray-600 dark:text-gray-400">Errors</span>
          <span className={`font-medium ${health.metrics.errors > 0 ? 'text-red-500' : ''}`}>
            {health.metrics.errors.toLocaleString()}
          </span>
        </div>
        <div className="flex justify-between text-sm mt-1">
          <span className="text-gray-600 dark:text-gray-400">Error Rate</span>
          <span className={`font-medium ${health.metrics.errors / health.metrics.requests > 0.05 ? 'text-red-500' : ''}`}>
            {health.metrics.requests > 0 ? ((health.metrics.errors / health.metrics.requests) * 100).toFixed(2) : 0}%
          </span>
        </div>
      </div>
    </div>
  );
};

interface MetricCardProps {
  icon: React.ReactNode;
  label: string;
  value: string;
  status: 'success' | 'info' | 'warning' | 'error';
}

const MetricCard: React.FC<MetricCardProps> = ({ icon, label, value, status }) => {
  const statusColors = {
    success: 'text-green-500',
    info: 'text-blue-500',
    warning: 'text-yellow-500',
    error: 'text-red-500'
  };

  return (
    <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-3">
      <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
        {icon}
        <span>{label}</span>
      </div>
      <div className={`text-lg font-bold ${statusColors[status]}`}>
        {value}
      </div>
    </div>
  );
};

interface ServiceStatusProps {
  name: string;
  status: 'up' | 'down' | 'degraded';
  latency: number;
}

const ServiceStatus: React.FC<ServiceStatusProps> = ({ name, status, latency }) => {
  const statusColors = {
    up: 'text-green-500',
    down: 'text-red-500',
    degraded: 'text-yellow-500'
  };

  const statusDots = {
    up: 'bg-green-500',
    down: 'bg-red-500',
    degraded: 'bg-yellow-500'
  };

  return (
    <div className="flex items-center justify-between bg-gray-50 dark:bg-gray-700/50 rounded-lg px-3 py-2">
      <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
        {name}
      </span>
      <div className="flex items-center gap-2">
        <span className="text-xs text-gray-500 dark:text-gray-400">
          {latency}ms
        </span>
        <div className={`w-2 h-2 rounded-full ${statusDots[status]}`} />
      </div>
    </div>
  );
};

function formatUptime(seconds: number): string {
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  
  const parts = [];
  if (days > 0) parts.push(`${days}d`);
  if (hours > 0) parts.push(`${hours}h`);
  if (minutes > 0) parts.push(`${minutes}m`);
  if (parts.length === 0) parts.push('< 1m');
  
  return parts.join(' ');
}