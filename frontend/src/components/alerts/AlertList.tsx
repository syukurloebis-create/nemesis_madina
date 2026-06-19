// src/components/alerts/AlertList.tsx
import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import { Bell, AlertCircle, CheckCircle } from 'lucide-react';

interface Alert {
  id: string;
  type: 'fraud' | 'integrity' | 'custody' | 'system';
  severity: 'critical' | 'high' | 'medium' | 'low';
  title: string;
  description: string;
  timestamp: string;
  acknowledged: boolean;
}

const AlertList: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAlerts();
    const interval = setInterval(loadAlerts, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadAlerts = async () => {
    try {
      const allIntegrity = await api.verifyAllIntegrity();
      const mockAlerts: Alert[] = [];
      
      if (allIntegrity.failed_cases > 0) {
        mockAlerts.push({
          id: '1',
          type: 'integrity',
          severity: 'critical',
          title: 'Chain Integrity Issue Detected',
          description: `${allIntegrity.failed_cases} case(s) have broken hash chain`,
          timestamp: new Date().toISOString(),
          acknowledged: false
        });
      }
      
      setAlerts(mockAlerts);
    } catch (error) {
      console.error('Error loading alerts:', error);
    } finally {
      setLoading(false);
    }
  };

  const acknowledgeAlert = async (alertId: string) => {
    try {
      await api.acknowledgeAlert(alertId);
      setAlerts(prev => prev.map(a => 
        a.id === alertId ? { ...a, acknowledged: true } : a
      ));
    } catch (error) {
      console.error('Error acknowledging alert:', error);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-100 text-red-800';
      default: return 'bg-yellow-100 text-yellow-800';
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6 animate-pulse">
        <div className="h-32 bg-gray-200 rounded"></div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="px-4 py-3 border-b border-gray-200 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <Bell className="w-5 h-5 text-gray-500" />
          <h3 className="text-lg font-semibold text-gray-900">Alerts</h3>
          {alerts.filter(a => !a.acknowledged).length > 0 && (
            <span className="px-2 py-0.5 text-xs rounded-full bg-red-500 text-white">
              {alerts.filter(a => !a.acknowledged).length}
            </span>
          )}
        </div>
      </div>

      <div className="divide-y divide-gray-200">
        {alerts.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            <CheckCircle className="w-12 h-12 mx-auto mb-2 text-green-500" />
            <p>No active alerts</p>
            <p className="text-sm">System is healthy</p>
          </div>
        ) : (
          alerts.map((alert) => (
            <div key={alert.id} className={`p-4 ${alert.acknowledged ? 'opacity-50' : ''}`}>
              <div className="flex items-start gap-3">
                <div className={`p-2 rounded-full ${getSeverityColor(alert.severity)}`}>
                  <AlertCircle className="w-4 h-4" />
                </div>
                <div className="flex-1">
                  <h4 className="font-medium text-gray-900">{alert.title}</h4>
                  <p className="text-sm text-gray-600 mt-1">{alert.description}</p>
                  {!alert.acknowledged && (
                    <button
                      onClick={() => acknowledgeAlert(alert.id)}
                      className="mt-2 text-sm text-blue-600 hover:text-blue-800"
                    >
                      Acknowledge
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default AlertList;