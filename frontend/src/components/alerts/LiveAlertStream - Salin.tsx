import React, { useState, useEffect } from 'react';
import { useAuthStore } from '../../stores/authStore';
import { wsService } from '../../services/websocket';

interface Alert {
  id: string;
  title: string;
  description: string;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  status: string;
  timestamp: string;
  entity_name?: string;
  case_id?: string;
}

const LiveAlertStream: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [stats, setStats] = useState({ total: 0, critical: 0, high: 0 });
  const { token } = useAuthStore();

  useEffect(() => {
    if (token) {
      fetchInitialAlerts();
      connectWebSocket();
    }
    
    return () => {
      wsService.disconnect();
    };
  }, [token]);

  const fetchInitialAlerts = async () => {
    try {
      const response = await fetch('http://localhost/alerts/?limit=20', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        const alertsList = Array.isArray(data) ? data : data.data || [];
        setAlerts(alertsList);
        updateStats(alertsList);
      }
    } catch (error) {
      console.error('Failed to fetch alerts:', error);
    }
  };

  const connectWebSocket = () => {
    wsService.connect(token!);
    wsService.on('new_alert', (alert: Alert) => {
      setAlerts(prev => [alert, ...prev].slice(0, 50));
      updateStats([alert, ...alerts]);
    });
    wsService.on('alert_update', (data: { alert_id: string; status: string }) => {
      setAlerts(prev => prev.map(alert => 
        alert.id === data.alert_id ? { ...alert, status: data.status } : alert
      ));
    });
    
    setIsConnected(true);
  };

  const updateStats = (alertsList: Alert[]) => {
    setStats({
      total: alertsList.length,
      critical: alertsList.filter(a => a.severity === 'critical').length,
      high: alertsList.filter(a => a.severity === 'high').length,
    });
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical': return '🔴';
      case 'high': return '🟠';
      case 'medium': return '🟡';
      case 'low': return '🟢';
      default: return '🔵';
    }
  };

  const getSeverityClass = (severity: string) => {
    switch (severity) {
      case 'critical': return 'border-red-500 bg-red-500/5';
      case 'high': return 'border-orange-500 bg-orange-500/5';
      case 'medium': return 'border-yellow-500 bg-yellow-500/5';
      case 'low': return 'border-green-500 bg-green-500/5';
      default: return 'border-gray-500 bg-gray-500/5';
    }
  };

  const acknowledgeAlert = async (alertId: string) => {
    try {
      await fetch(`http://localhost/alerts/${alertId}/acknowledge`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ alert_id: alertId, user: 'admin' })
      });
    } catch (error) {
      console.error('Failed to acknowledge alert:', error);
    }
  };

  return (
    <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-700">
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-3">
            <h2 className="text-lg font-semibold text-white">🚨 Live Alert Stream</h2>
            <div className="flex items-center gap-1">
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
              <span className="text-xs text-gray-500">{isConnected ? 'Connected' : 'Disconnected'}</span>
            </div>
          </div>
          <div className="flex gap-4 text-sm">
            <span className="text-gray-400">Total: <span className="text-white font-bold">{stats.total}</span></span>
            <span className="text-gray-400">Critical: <span className="text-red-500 font-bold">{stats.critical}</span></span>
            <span className="text-gray-400">High: <span className="text-orange-500 font-bold">{stats.high}</span></span>
          </div>
        </div>
      </div>
      
      <div className="h-[400px] overflow-y-auto">
        {alerts.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-500">
            No alerts. System is healthy.
          </div>
        ) : (
          alerts.map((alert) => (
            <div
              key={alert.id}
              className={`p-4 border-b border-gray-700 hover:bg-gray-700/30 transition-colors cursor-pointer ${getSeverityClass(alert.severity)} border-l-4`}
              onClick={() => acknowledgeAlert(alert.id)}
            >
              <div className="flex items-start gap-3">
                <span className="text-xl">{getSeverityIcon(alert.severity)}</span>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`text-xs font-bold px-2 py-0.5 rounded ${alert.severity === 'critical' ? 'bg-red-500/20 text-red-400' : 'bg-gray-700 text-gray-400'}`}>
                      {alert.severity.toUpperCase()}
                    </span>
                    <span className="text-xs text-gray-500">
                      {alert.status}
                    </span>
                    {alert.entity_name && (
                      <span className="text-xs text-gray-500">🏢 {alert.entity_name}</span>
                    )}
                  </div>
                  <h4 className="font-semibold text-white text-sm">{alert.title}</h4>
                  <p className="text-xs text-gray-400 mt-1">{alert.description}</p>
                  <div className="flex justify-between items-center mt-2">
                    <span className="text-xs text-gray-500">
                      {new Date(alert.timestamp).toLocaleTimeString()}
                    </span>
                    {alert.status === 'new' && (
                      <span className="text-xs text-blue-400 animate-pulse">Click to acknowledge</span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default LiveAlertStream;
